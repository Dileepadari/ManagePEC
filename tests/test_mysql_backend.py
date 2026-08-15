"""Opt-in tests against a real MySQL or MariaDB server.

Skipped unless a scratch database is pointed at explicitly, because they DROP and
recreate every table in it:

    MANAGEPEC_TEST_MYSQL_DB=managepec_test \\
    MANAGEPEC_TEST_MYSQL_USER=managepec_test \\
    MANAGEPEC_TEST_MYSQL_PASSWORD=secret \\
    pytest tests/test_mysql_backend.py

The SQLite suite covers the same behaviour; these exist to prove the dialect
translation (placeholders, MONTH(), the ESCAPE clause) and the ON DELETE rules
behave identically on the server the project was originally written for.
"""

from __future__ import annotations

import os

import pytest

from managepec import presets, repository as repo, safe_sql
from managepec.config import Settings
from managepec.db import Database
from managepec.models import StudentInput

pytest.importorskip("pymysql")

TEST_DB = os.environ.get("MANAGEPEC_TEST_MYSQL_DB")

pytestmark = pytest.mark.skipif(
    not TEST_DB,
    reason="set MANAGEPEC_TEST_MYSQL_DB to run the MySQL backend tests",
)


@pytest.fixture(scope="module")
def mysql_database() -> Database:
    settings = Settings(
        backend="mysql",
        mysql_host=os.environ.get("MANAGEPEC_TEST_MYSQL_HOST", "localhost"),
        mysql_port=int(os.environ.get("MANAGEPEC_TEST_MYSQL_PORT", "3306")),
        mysql_user=os.environ.get("MANAGEPEC_TEST_MYSQL_USER", "root"),
        mysql_password=os.environ.get("MANAGEPEC_TEST_MYSQL_PASSWORD", ""),
        mysql_database=TEST_DB or "",
    )
    return Database(settings)


@pytest.fixture()
def my(mysql_database: Database):
    """A freshly seeded connection, so each test starts from the same rows."""
    conn = mysql_database.connect()
    mysql_database.initialise(conn, with_seed=True)
    yield conn
    conn.close()


def test_dialect_is_mysql(my):
    assert my.dialect == "mysql"


def test_schema_and_seed_load(my):
    assert my.scalar("SELECT COUNT(*) FROM SPORTS") == 7
    assert my.scalar("SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS") == 12
    assert my.scalar("SELECT COUNT(*) FROM STAFF_DETAILS") == 8


def test_placeholders_are_translated(my):
    row = my.query_one("SELECT Sport_Name FROM SPORTS WHERE Sport_ID = ?", (1,))
    assert row["Sport_Name"] == "Football"


def test_month_function_matches_sqlite_results(my):
    assert repo.funds_released_in_month(my, 2) == {
        "month": 2,
        "total": 10000,
        "releases": 2,
    }
    assert [row["Month"] for row in repo.funds_by_month(my)] == [1, 2, 3, 4, 5]


def test_aggregates_match(my):
    assert repo.total_pending_salary(my) == 130000
    assert repo.average_students_per_sport(my) == pytest.approx(11 / 7, abs=0.01)


def test_search_is_not_injectable(my):
    assert repo.search_sport_by_name(my, "x' OR '1'='1") == []
    assert my.scalar("SELECT COUNT(*) FROM SPORTS") == 7


def test_like_wildcards_are_escaped(my):
    assert len(repo.search_challenges(my, "Challenge")) == 6
    assert repo.search_challenges(my, "%") == []


def test_every_saved_query_runs(my):
    for preset in presets.presets(my.dialect):
        columns, rows, _truncated = safe_sql.run(my, preset.sql, 500)
        assert isinstance(rows, list)
        if rows:
            assert columns


def test_insert_writes_all_three_tables(my):
    repo.add_student(
        my,
        StudentInput.from_raw(
            {
                "student_id": "90",
                "name": "Mysql Tester",
                "date_of_birth": "2005-01-01",
                "contact": "+91-9800000001",
                "department": "CSE",
                "course_year": "2024",
                "credits_done": "0",
                "assigned_sport": "1",
                "attendance": "55",
            }
        ),
    )
    assert my.scalar(
        "SELECT COUNT(*) FROM STUDENT_ACAD_DETAILS WHERE Student_ID = 90"
    ) == 1


def test_retiring_a_sport_keeps_the_dependent_records(my):
    repo.remove_sport(my, 1)
    assert my.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 1"
    ) == 1
    assert my.scalar(
        "SELECT Assigned_Sport FROM STUDENT_SPORT_DETAILS WHERE Student_ID = 1"
    ) is None
    assert my.scalar("SELECT Sport_ID FROM STAFF_POSITION WHERE Staff_ID = 1") is None
    assert my.scalar("SELECT COUNT(*) FROM SPORTS_SLOT WHERE Sport_ID = 1") == 0


def test_retiring_equipment_keeps_the_funding_row(my):
    repo.remove_equipment(my, 2)
    assert my.scalar("SELECT COUNT(*) FROM EQUIPMENT WHERE Equipment_ID = 2") == 0
    assert my.scalar(
        "SELECT COUNT(*) FROM EQUIPMENT_FUNDS WHERE Transaction_ID = 2"
    ) == 1
    assert my.scalar(
        "SELECT Equipment_ID FROM EQUIPMENT_FUNDS WHERE Transaction_ID = 2"
    ) is None
