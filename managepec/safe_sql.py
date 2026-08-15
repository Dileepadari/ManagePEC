"""Guard for the ad-hoc query console in the web app.

The console exists so that a coach or the PEC head can run a SELECT without
opening a shell.  It is not an admin console, so anything that could change or
leak the database is rejected before it reaches the driver:

* exactly one statement, so `SELECT 1; DROP TABLE SPORTS` cannot get through
* the statement must open with SELECT or WITH
* no write, DDL, or file/engine keyword anywhere outside a string literal
* results are capped, so a cross join cannot exhaust the process

Comments and string literals are blanked out before the keyword scan, which
stops `SELECT/*x*/ 1 UNION SELECT ... INTO OUTFILE` style smuggling.
"""

from __future__ import annotations

import re

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


def _describe(words: list[str]) -> UnsafeQuery | None:
    """Build the refusal for the first forbidden keyword found, if any."""
    for word in words:
        if word in WRITE_KEYWORDS:
            return UnsafeQuery(
                f"This statement would change data in the database ({word.upper()}). "
                "The query console is read-only, so nothing was run and no rows "
                "were touched. Use the Students, Staff, Sports, Challenges or "
                "Equipment pages to make changes.",
                "changes-data",
            )
        if word in SCHEMA_KEYWORDS:
            return UnsafeQuery(
                f"This statement would change the database schema ({word.upper()}). "
                "The query console is read-only, so nothing was run and the "
                "schema is unchanged. Schema changes belong in schema/, applied "
                "with `python -m managepec.cli init-db`.",
                "changes-schema",
            )
        if word in SESSION_KEYWORDS:
            return UnsafeQuery(
                f"This statement would change server, session or file state "
                f"({word.upper()}), which the query console does not allow. "
                "Nothing was run.",
                "changes-state",
            )
    return None


def validate(sql: str) -> str:
    """Return the cleaned statement, or raise UnsafeQuery explaining the refusal."""
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
            "could change the database, so the whole submission was refused.",
            "multiple",
        )

    words = [word.lower() for word in _WORD_RE.findall(scrubbed)]
    if not words:
        raise UnsafeQuery("Enter a query first.", "empty")

    # Checked before the SELECT test so a write gets its own explanation rather
    # than the generic "not a SELECT".
    refusal = _describe(words)
    if refusal is not None:
        raise refusal

    if words[0] not in {"select", "with"}:
        raise UnsafeQuery(
            "Only SELECT and WITH queries can run here.", "not-a-select"
        )

    return statement.rstrip().rstrip(";")


def run(conn: Connection, sql: str, limit: int = 500) -> tuple[list[str], list[Row], bool]:
    """Validate and run a query.

    Returns the column names, the rows (at most `limit` of them) and whether the
    result was cut short.
    """
    statement = validate(sql)
    rows = conn.query(statement)
    truncated = len(rows) > limit
    rows = rows[:limit]
    columns = list(rows[0].keys()) if rows else []
    return columns, rows, truncated


__all__ = ["FORBIDDEN_KEYWORDS", "UnsafeQuery", "run", "strip_literals_and_comments", "validate"]
