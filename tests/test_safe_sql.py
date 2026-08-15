"""Tests for the read-only guard on the query console."""

from __future__ import annotations

import pytest

from managepec import safe_sql
from managepec.safe_sql import UnsafeQuery, strip_literals_and_comments, validate


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1",
        "select Sport_Name from SPORTS",
        "  SELECT * FROM SPORTS;  ",
        "WITH t AS (SELECT 1 AS a) SELECT a FROM t",
        "SELECT Sport_Name FROM SPORTS WHERE Sport_Name LIKE '%ball%'",
    ],
)
def test_read_only_queries_pass(sql):
    assert validate(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM SPORTS",
        "DROP TABLE SPORTS",
        "UPDATE SPORTS SET Capacity = 0",
        "INSERT INTO SPORTS VALUES (9, 'x', 1, 0, NULL)",
        "ALTER TABLE SPORTS ADD COLUMN x INT",
        "PRAGMA table_info(SPORTS)",
        "ATTACH DATABASE '/etc/passwd' AS leak",
        "VACUUM",
        "CREATE TABLE t (a INT)",
    ],
)
def test_write_and_ddl_statements_are_refused(sql):
    with pytest.raises(UnsafeQuery):
        validate(sql)


def test_stacked_statements_are_refused():
    with pytest.raises(UnsafeQuery, match="one statement"):
        validate("SELECT 1; DROP TABLE SPORTS")


def test_trailing_semicolon_is_allowed():
    assert validate("SELECT 1;") == "SELECT 1"


def test_comment_hidden_keywords_are_caught():
    with pytest.raises(UnsafeQuery):
        validate("SELECT 1 /* harmless */ UNION SELECT 1 INTO OUTFILE '/tmp/x'")


def test_a_keyword_inside_a_literal_is_not_a_refusal():
    assert validate("SELECT 'we should drop by' AS note")


def test_blank_input_is_refused():
    with pytest.raises(UnsafeQuery):
        validate("   ")


def test_strip_literals_preserves_length():
    sql = "SELECT 'abc' -- note\nFROM T"
    assert len(strip_literals_and_comments(sql)) == len(sql)


def test_strip_literals_blanks_block_comments():
    stripped = strip_literals_and_comments("SELECT /* drop */ 1")
    assert "drop" not in stripped


def test_run_returns_columns_and_rows(conn):
    columns, rows, truncated = safe_sql.run(
        conn, "SELECT Sport_ID, Sport_Name FROM SPORTS ORDER BY Sport_ID", 100
    )
    assert columns == ["Sport_ID", "Sport_Name"]
    assert rows[0]["Sport_Name"] == "Football"
    assert truncated is False


def test_run_caps_the_row_count(conn):
    _columns, rows, truncated = safe_sql.run(conn, "SELECT * FROM SPORTS", 2)
    assert len(rows) == 2
    assert truncated is True


def test_run_refuses_a_write(conn):
    with pytest.raises(UnsafeQuery):
        safe_sql.run(conn, "DELETE FROM SPORTS", 10)
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7
