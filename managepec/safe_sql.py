"""Guard for the ad-hoc query console in the web app.

Every submission is classified before anything reaches the driver:

* **read** - a single SELECT or WITH. Runs straight away, capped at a row limit
  so a cross join cannot exhaust the process.
* **changes-data / changes-schema** - a write or DDL. Refused on the first
  submission with a warning naming what it would do; the caller can then pass
  `confirmed=True` to run it deliberately. Nothing is ever written by accident.
* **never allowed** - more than one statement (`SELECT 1; DROP TABLE SPORTS`),
  or anything touching server, session or file state (ATTACH, INTO OUTFILE,
  GRANT). These escape the database rather than change it, so no confirmation
  unlocks them.

Comments and string literals are blanked out before the keyword scan, which
stops `SELECT/*x*/ 1 UNION SELECT ... INTO OUTFILE` style smuggling.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .db import Connection, Row

# Grouped by what the statement would actually do, so the refusal can say so
# rather than just naming a banned word.
WRITE_KEYWORDS = frozenset(
    {"delete", "insert", "merge", "replace", "truncate", "update", "upsert"}
)

SCHEMA_KEYWORDS = frozenset(
    {"alter", "create", "drop", "reindex", "rename", "vacuum"}
)

SESSION_KEYWORDS = frozenset(
    {
        "attach",
        "begin",
        "benchmark",
        "call",
        "commit",
        "copy",
        "detach",
        "do",
        "dumpfile",
        "execute",
        "grant",
        "handler",
        "into",
        "load",
        "load_file",
        "lock",
        "outfile",
        "pragma",
        "release",
        "revoke",
        "rollback",
        "savepoint",
        "set",
        "shutdown",
        "sleep",
        "start",
        "unlock",
    }
)

FORBIDDEN_KEYWORDS = WRITE_KEYWORDS | SCHEMA_KEYWORDS | SESSION_KEYWORDS

_WORD_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")


class UnsafeQuery(ValueError):
    """The submitted SQL is not a plain, single, read-only SELECT.

    `kind` says why, so the page can warn loudly about a statement that would
    have changed the database and stay quiet about a typo:

        changes-data    an INSERT/UPDATE/DELETE and friends
        changes-schema  DDL
        changes-state   touches the server, session or filesystem
        not-a-select    does not open with SELECT or WITH
        multiple        more than one statement
        empty           nothing submitted
    """

    def __init__(self, message: str, kind: str = "not-a-select") -> None:
        super().__init__(message)
        self.kind = kind

    @property
    def changes_database(self) -> bool:
        return self.kind in {"changes-data", "changes-schema"}


def strip_literals_and_comments(sql: str) -> str:
    """Replace string literals and comments with spaces, keeping the length.

    Keeping the length means an offset in the result still lines up with the
    original text, which makes the error messages honest.
    """
    out: list[str] = []
    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < n else ""

        if ch in {"'", '"', "`"}:
            quote = ch
            out.append(" ")
            i += 1
            while i < n:
                if sql[i] == quote:
                    if i + 1 < n and sql[i + 1] == quote:
                        out.append("  ")
                        i += 2
                        continue
                    out.append(" ")
                    i += 1
                    break
                out.append(" ")
                i += 1
            continue

        if ch == "-" and nxt == "-":
            while i < n and sql[i] != "\n":
                out.append(" ")
                i += 1
            continue

        if ch == "#":
            while i < n and sql[i] != "\n":
                out.append(" ")
                i += 1
            continue

        if ch == "/" and nxt == "*":
            out.append("  ")
            i += 2
            while i < n and not (sql[i] == "*" and i + 1 < n and sql[i + 1] == "/"):
                out.append(" ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue

        out.append(ch)
        i += 1
    return "".join(out)


@dataclass(frozen=True)
class Plan:
    """What a submitted statement is, decided before anything runs."""

    statement: str
    kind: str  # "read" | "changes-data" | "changes-schema"
    keyword: str | None = None
    warning: str | None = None

    @property
    def changes_database(self) -> bool:
        return self.kind in {"changes-data", "changes-schema"}


@dataclass(frozen=True)
class Result:
    """What running a statement produced."""

    kind: str
    columns: list[str] = field(default_factory=list)
    rows: list[Row] = field(default_factory=list)
    truncated: bool = False
    rowcount: int = 0
    message: str = ""


def _classify(statement: str, words: list[str]) -> Plan:
    """Decide what the statement does, or raise for the never-allowed cases."""
    for word in words:
        if word in SESSION_KEYWORDS:
            raise UnsafeQuery(
                f"This statement would change server, session or file state "
                f"({word.upper()}). That is outside what this console can do at "
                "all, so it was not run and cannot be confirmed.",
                "changes-state",
            )
        if word in WRITE_KEYWORDS:
            return Plan(
                statement,
                "changes-data",
                word.upper(),
                f"This will change data in the database ({word.upper()}). It has "
                "not been run yet. Check the statement, and confirm below only if "
                "you are sure - the change cannot be undone from here.",
            )
        if word in SCHEMA_KEYWORDS:
            return Plan(
                statement,
                "changes-schema",
                word.upper(),
                f"This will change the database schema ({word.upper()}). It has "
                "not been run yet. Schema changes normally belong in schema/ so "
                "they survive a rebuild; confirm below only if you meant to "
                "change this database in place.",
            )

    if words[0] not in {"select", "with"}:
        raise UnsafeQuery(
            f"{words[0].upper()} is not something this console runs. Statements "
            "must start with SELECT or WITH, or be a write this console can "
            "confirm.",
            "not-a-select",
        )
    return Plan(statement, "read")


def plan(sql: str) -> Plan:
    """Classify a submission, raising UnsafeQuery for what is never allowed."""
    if sql is None or not sql.strip():
        raise UnsafeQuery("Enter a query first.", "empty")

    statement = sql.strip()
    scrubbed = strip_literals_and_comments(statement)

    body = scrubbed.rstrip()
    if body.endswith(";"):
        body = body[:-1]
    if ";" in body:
        raise UnsafeQuery(
            "Run one statement at a time. A second statement after a semicolon "
            "cannot be reviewed on its own, so the whole submission was refused.",
            "multiple",
        )

    words = [word.lower() for word in _WORD_RE.findall(scrubbed)]
    if not words:
        raise UnsafeQuery("Enter a query first.", "empty")

    return _classify(statement.rstrip().rstrip(";"), words)


class ConfirmationRequired(Exception):
    """A write was submitted without confirmation. Carries the plan to show."""

    def __init__(self, plan: Plan) -> None:
        super().__init__(plan.warning or "This statement changes the database.")
        self.plan = plan


def validate(sql: str) -> str:
    """Read-only check: return the statement, or raise unless it is a SELECT.

    Used where a write is never acceptable - the saved-query page runs its
    presets through this.
    """
    checked = plan(sql)
    if checked.kind != "read":
        raise UnsafeQuery(checked.warning or "This statement changes the database.",
                          checked.kind)
    return checked.statement


def run(
    conn: Connection,
    sql: str,
    limit: int = 500,
    confirmed: bool = False,
) -> Result:
    """Run a submission.

    Reads run immediately. A write runs only when `confirmed` is true; otherwise
    `ConfirmationRequired` is raised carrying the warning to show the user.
    """
    checked = plan(sql)

    if checked.kind == "read":
        rows = conn.query(checked.statement)
        truncated = len(rows) > limit
        rows = rows[:limit]
        columns = list(rows[0].keys()) if rows else []
        return Result("read", columns, rows, truncated)

    if not confirmed:
        raise ConfirmationRequired(checked)

    with conn.transaction():
        affected = conn.execute(checked.statement)

    noun = "row" if affected == 1 else "rows"
    return Result(
        checked.kind,
        rowcount=affected,
        message=(
            f"{checked.keyword} ran. {affected} {noun} changed."
            if checked.kind == "changes-data"
            else f"{checked.keyword} ran. The schema was changed."
        ),
    )


__all__ = [
    "FORBIDDEN_KEYWORDS",
    "ConfirmationRequired",
    "Plan",
    "Result",
    "SCHEMA_KEYWORDS",
    "SESSION_KEYWORDS",
    "UnsafeQuery",
    "WRITE_KEYWORDS",
    "plan",
    "run",
    "strip_literals_and_comments",
    "validate",
]
