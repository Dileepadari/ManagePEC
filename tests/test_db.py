"""Tests for the connection layer: placeholders, script splitting, schema load."""

from __future__ import annotations

import pytest

from managepec.db import month_expr, split_statements, translate_placeholders

TABLES = [
    "EQUIPMENT",
    "EQUIPMENT_FUNDS",
    "EQUIPMENT_MAINTENANCE",
    "EQUIPMENT_REGISTRATION",
    "FITNESS_CHALLENGES",
    "FITNESS_CHALLENGES_DETAILS",
    "FITNESS_CHALLENGE_MENTORS",
    "FITNESS_CHALLENGE_WINNERS",
    "FITNESS_SECTIONS",
    "FITNESS_SECTIONS_DETAILS",
    "FUNDS",
    "MEDICAL_HISTORY",
    "MEDICAL_HISTORY_DETAILS",
    "SPORTS",
    "SPORTS_LOCATION",
    "SPORTS_SLOT",
    "STAFF_DETAILS",
    "STAFF_POSITION",
    "STAFF_PROFESSIONAL",
    "STAFF_TASKS",
    "STUDENT_ACAD_DETAILS",
    "STUDENT_HEALTH_DETAILS",
    "STUDENT_PERSONAL_DETAILS",
    "STUDENT_SPORT_DETAILS",
    "TRANSACTIONS",
]


def test_sqlite_keeps_question_marks():
    assert translate_placeholders("SELECT ? FROM T", "sqlite") == "SELECT ? FROM T"


def test_mysql_rewrites_placeholders():
    assert translate_placeholders("SELECT ? FROM T", "mysql") == "SELECT %s FROM T"


def test_mysql_leaves_question_marks_inside_literals():
    sql = "SELECT * FROM T WHERE Note = 'why?' AND Id = ?"
    assert translate_placeholders(sql, "mysql") == (
        "SELECT * FROM T WHERE Note = 'why?' AND Id = %s"
    )


def test_mysql_doubles_percent_signs():
    sql = "SELECT * FROM T WHERE Name LIKE '%a%' AND Id = ?"
    assert translate_placeholders(sql, "mysql") == (
        "SELECT * FROM T WHERE Name LIKE '%%a%%' AND Id = %s"
    )


def test_escaped_quote_inside_literal_is_preserved():
    sql = "SELECT 'it''s ok' WHERE Id = ?"
    assert translate_placeholders(sql, "mysql") == "SELECT 'it''s ok' WHERE Id = %s"


def test_split_statements_ignores_semicolons_in_strings_and_comments():
    script = """
    -- a comment with a ; in it
    INSERT INTO T VALUES ('a;b');
    SELECT 1;
    """
    statements = split_statements(script)
    assert len(statements) == 2
    assert "a;b" in statements[0]
    assert statements[1].endswith("SELECT 1")


def test_split_statements_drops_comment_only_fragments():
    assert split_statements("-- only a comment\n") == []


def test_month_expr_differs_per_dialect():
    assert "strftime" in month_expr("sqlite", "f.Date")
    assert month_expr("mysql", "f.Date") == "MONTH(f.Date)"


def test_schema_creates_every_table(conn):
    names = {
        row["name"]
        for row in conn.query("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    missing = [table for table in TABLES if table not in names]
    assert missing == []


def test_seed_loads_rows(conn):
    assert conn.scalar("SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS") == 12
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7
    assert conn.scalar("SELECT COUNT(*) FROM STAFF_DETAILS") == 8


def test_foreign_keys_are_enforced(conn):
    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO STUDENT_ACAD_DETAILS "
            "(Student_ID, Department, Course_Year, Credits_Done) VALUES (?, ?, ?, ?)",
            (999, "CSE", "2024", 0),
        )


def test_transaction_rolls_back_on_error(conn):
    before = conn.scalar("SELECT COUNT(*) FROM SPORTS")
    with pytest.raises(RuntimeError):
        with conn.transaction():
            conn.execute(
                "INSERT INTO SPORTS (Sport_ID, Sport_Name, Capacity, "
                "No_of_Participants) VALUES (?, ?, ?, ?)",
                (99, "Kabaddi", 30, 0),
            )
            raise RuntimeError("boom")
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == before
