"""Database access layer.

The rest of the application writes SQL once, using `?` placeholders, and this
module adapts it to whichever backend is configured:

    sqlite  - the default, no server needed, used by the tests
    mysql   - the original phase-4 target, via PyMySQL

Two things are normalised here so callers never branch on the backend:

* placeholders, `?` is rewritten to `%s` for MySQL (string literals are skipped)
* rows, both backends hand back plain dicts keyed by column name

Every statement goes through `execute`/`query` with a parameter tuple.  There is
no string interpolation of user input anywhere in the codebase, which is what
made the phase-4 script trivially injectable.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from .config import SCHEMA_DIR, Settings, load_settings

Params = Sequence[Any]
Row = dict[str, Any]


class DatabaseError(RuntimeError):
    """Raised for configuration and connection problems we can explain."""


def translate_placeholders(sql: str, dialect: str) -> str:
    """Rewrite `?` placeholders for the target dialect.

    Only `?` outside single-quoted string literals is touched, so a query such
    as ``WHERE Name LIKE '%?%'`` keeps its literal intact.
    """
    if dialect == "sqlite":
        return sql

    out: list[str] = []
    in_string = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        if in_string:
            if ch == "'":
                # '' is an escaped quote inside a literal.
                if i + 1 < len(sql) and sql[i + 1] == "'":
                    out.append("''")
                    i += 2
                    continue
                in_string = False
                out.append(ch)
            elif ch == "%":
                # PyMySQL %-formats the whole statement, literals included.
                out.append("%%")
            else:
                out.append(ch)
        elif ch == "'":
            in_string = True
            out.append(ch)
        elif ch == "?":
            out.append("%s")
        elif ch == "%":
            out.append("%%")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


class Connection:
    """Thin wrapper giving both backends the same small API."""

    def __init__(self, raw: Any, dialect: str) -> None:
        self._raw = raw
        self.dialect = dialect

    # ------------------------------------------------------------- statements

    def query(self, sql: str, params: Params = ()) -> list[Row]:
        """Run a SELECT and return every row as a dict."""
        cursor = self._cursor()
        try:
            cursor.execute(translate_placeholders(sql, self.dialect), tuple(params))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def query_one(self, sql: str, params: Params = ()) -> Row | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def scalar(self, sql: str, params: Params = ()) -> Any:
        row = self.query_one(sql, params)
        if row is None:
            return None
        return next(iter(row.values()))

    def execute(self, sql: str, params: Params = ()) -> int:
        """Run one INSERT/UPDATE/DELETE and return the affected row count."""
        cursor = self._cursor()
        try:
            cursor.execute(translate_placeholders(sql, self.dialect), tuple(params))
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, sql: str, seq: Iterable[Params]) -> int:
        cursor = self._cursor()
        try:
            cursor.executemany(
                translate_placeholders(sql, self.dialect), [tuple(p) for p in seq]
            )
            return cursor.rowcount
        finally:
            cursor.close()

    def executescript(self, script: str) -> None:
        """Run a multi-statement script (schema and seed files)."""
        if self.dialect == "sqlite":
            self._raw.executescript(script)
            return
        cursor = self._cursor()
        try:
            for statement in split_statements(script):
                cursor.execute(statement)
        finally:
            cursor.close()

    # ----------------------------------------------------------- transactions

    def commit(self) -> None:
        self._raw.commit()

    def rollback(self) -> None:
        self._raw.rollback()

    def close(self) -> None:
        self._raw.close()

    @contextmanager
    def transaction(self) -> Iterator["Connection"]:
        """Commit on clean exit, roll back on any exception."""
        try:
            yield self
        except Exception:
            self.rollback()
            raise
        else:
            self.commit()

    # ---------------------------------------------------------------- helpers

    def _cursor(self) -> Any:
        return self._raw.cursor()

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def split_statements(script: str) -> list[str]:
    """Split a SQL script on semicolons that are not inside a string or comment."""
    statements: list[str] = []
    current: list[str] = []
    in_string = False
    in_line_comment = False
    i = 0
    while i < len(script):
        ch = script[i]
        nxt = script[i + 1] if i + 1 < len(script) else ""

        if in_line_comment:
            current.append(ch)
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_string:
            current.append(ch)
            if ch == "'":
                if nxt == "'":
                    current.append(nxt)
                    i += 2
                    continue
                in_string = False
            i += 1
            continue

        if ch == "-" and nxt == "-":
            in_line_comment = True
            current.append(ch)
            i += 1
            continue

        if ch == "'":
            in_string = True
            current.append(ch)
            i += 1
            continue

        if ch == ";":
            statements.append("".join(current))
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    statements.append("".join(current))
    return [s.strip() for s in statements if _has_sql(s)]


def _has_sql(statement: str) -> bool:
    """True when the fragment holds something other than blanks and comments."""
    for line in statement.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            return True
    return False


class Database:
    """Opens connections against the configured backend."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()

    @property
    def dialect(self) -> str:
        return self.settings.backend

    def connect(self) -> Connection:
        if self.settings.backend == "sqlite":
            return self._connect_sqlite()
        return self._connect_mysql()

    def _connect_sqlite(self) -> Connection:
        path = self.settings.sqlite_path
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        raw = sqlite3.connect(str(path))
        raw.row_factory = sqlite3.Row
        raw.execute("PRAGMA foreign_keys = ON")
        return Connection(raw, "sqlite")

    def _connect_mysql(self) -> Connection:
        try:
            import pymysql
            import pymysql.cursors
        except ImportError as exc:  # pragma: no cover - depends on the install
            raise DatabaseError(
                "MANAGEPEC_DB=mysql needs PyMySQL: pip install -r requirements.txt"
            ) from exc

        s = self.settings
        try:
            raw = pymysql.connect(
                host=s.mysql_host,
                port=s.mysql_port,
                user=s.mysql_user,
                password=s.mysql_password,
                database=s.mysql_database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
        except Exception as exc:  # pragma: no cover - needs a live server
            raise DatabaseError(
                f"could not connect to MySQL at {s.mysql_host}:{s.mysql_port} "
                f"as {s.mysql_user!r}: {exc}"
            ) from exc
        return Connection(raw, "mysql")

    # ------------------------------------------------------------ maintenance

    def schema_path(self) -> Path:
        return SCHEMA_DIR / f"schema.{self.dialect}.sql"

    def seed_path(self) -> Path:
        return SCHEMA_DIR / "seed.sql"

    def initialise(self, conn: Connection, with_seed: bool = True) -> None:
        """Create every table, optionally loading the sample data."""
        conn.executescript(self.schema_path().read_text(encoding="utf-8"))
        if with_seed:
            conn.executescript(self.seed_path().read_text(encoding="utf-8"))
        conn.commit()


def month_expr(dialect: str, column: str) -> str:
    """Dialect-specific 'month number of this date column' expression."""
    if dialect == "sqlite":
        return f"CAST(strftime('%m', {column}) AS INTEGER)"
    return f"MONTH({column})"


def year_expr(dialect: str, column: str) -> str:
    if dialect == "sqlite":
        return f"CAST(strftime('%Y', {column}) AS INTEGER)"
    return f"YEAR({column})"


__all__ = [
    "Connection",
    "Database",
    "DatabaseError",
    "Row",
    "month_expr",
    "split_statements",
    "translate_placeholders",
    "year_expr",
]
