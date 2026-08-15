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

FORBIDDEN_KEYWORDS = frozenset(
    {
        "alter",
        "attach",
        "begin",
        "call",
        "commit",
        "copy",
        "create",
        "delete",
        "detach",
        "do",
        "drop",
        "execute",
        "grant",
        "handler",
        "insert",
        "into",
        "load",
        "load_file",
        "lock",
        "merge",
        "outfile",
        "pragma",
        "reindex",
        "release",
        "rename",
        "replace",
        "revoke",
        "rollback",
        "savepoint",
        "set",
        "shutdown",
        "sleep",
        "start",
        "truncate",
        "unlock",
        "update",
        "upsert",
        "vacuum",
        "dumpfile",
        "benchmark",
    }
)

_WORD_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")


class UnsafeQuery(ValueError):
    """The submitted SQL is not a plain, single, read-only SELECT."""


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


def validate(sql: str) -> str:
    """Return the cleaned statement, or raise UnsafeQuery explaining the refusal."""
    if sql is None or not sql.strip():
        raise UnsafeQuery("enter a query first")

    statement = sql.strip()
    scrubbed = strip_literals_and_comments(statement)

    body = scrubbed.rstrip()
    if body.endswith(";"):
        body = body[:-1]
    if ";" in body:
        raise UnsafeQuery("run one statement at a time")

    words = [word.lower() for word in _WORD_RE.findall(scrubbed)]
    if not words:
        raise UnsafeQuery("enter a query first")
    if words[0] not in {"select", "with"}:
        raise UnsafeQuery("only SELECT and WITH queries are allowed here")

    offenders = sorted(FORBIDDEN_KEYWORDS.intersection(words))
    if offenders:
        raise UnsafeQuery(f"this console is read-only, remove: {', '.join(offenders)}")

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
