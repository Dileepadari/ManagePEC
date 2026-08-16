"""Tests for pagination and the confirm-to-run flow on the query console."""
from __future__ import annotations

import pytest

from managepec import safe_sql
from managepec.pagination import DEFAULT_PER_PAGE, Page


# ------------------------------------------------------------------ pagination


def test_page_slices_and_clamps():
    p = Page.of(list(range(1, 101)), 3, 25)
    assert p.items[0] == 51 and p.items[-1] == 75
    assert (p.number, p.pages, p.first_index, p.last_index) == (3, 4, 51, 75)


def test_page_number_past_the_end_clamps_to_the_last_page():
    assert Page.of(list(range(30)), 99, 25).number == 2


@pytest.mark.parametrize("bad", ["abc", "", None, "-4", "0"])
def test_bad_page_numbers_fall_back_to_one(bad):
    assert Page.of(list(range(30)), bad, 25).number == 1


def test_an_unsupported_page_size_falls_back_to_the_default():
    assert Page.of(list(range(30)), 1, 7).per_page == DEFAULT_PER_PAGE


def test_empty_list_is_page_one_of_one():
    p = Page.of([], 1, 25)
    assert (p.number, p.pages, p.total, p.first_index, p.needed) == (1, 1, 0, 0, False)


def test_pager_is_hidden_until_it_is_needed():
    assert Page.of(list(range(10)), 1, 25).needed is False
    assert Page.of(list(range(11)), 1, 25).needed is True


def test_numbers_collapse_with_a_gap_on_long_lists():
    numbers = Page.of(list(range(500)), 10, 10).numbers()
    assert numbers[0] == 1 and numbers[-1] == 50
    assert None in numbers
    assert 10 in numbers


# ------------------------------------------------------------- confirm to run


def test_a_select_is_planned_as_a_read():
    assert safe_sql.plan("SELECT 1").kind == "read"


def test_a_write_needs_confirmation_before_it_runs(conn):
    before = conn.scalar("SELECT Attendance FROM STUDENT_SPORT_DETAILS WHERE Student_ID = 1")
    with pytest.raises(safe_sql.ConfirmationRequired) as ask:
        safe_sql.run(conn, "UPDATE STUDENT_SPORT_DETAILS SET Attendance = 5", 50)
    assert ask.value.plan.kind == "changes-data"
    assert ask.value.plan.keyword == "UPDATE"
    assert "has not been run yet" in ask.value.plan.warning
    assert conn.scalar(
        "SELECT Attendance FROM STUDENT_SPORT_DETAILS WHERE Student_ID = 1"
    ) == before


def test_a_confirmed_write_runs_and_reports_the_rowcount(conn):
    result = safe_sql.run(
        conn, "UPDATE STUDENT_SPORT_DETAILS SET Attendance = 5", 50, confirmed=True
    )
    assert result.kind == "changes-data"
    assert result.rowcount == 12
    assert "12 rows changed" in result.message
    assert conn.scalar(
        "SELECT Attendance FROM STUDENT_SPORT_DETAILS WHERE Student_ID = 1"
    ) == 5


def test_session_statements_cannot_be_confirmed(conn):
    with pytest.raises(safe_sql.UnsafeQuery) as exc:
        safe_sql.run(conn, "ATTACH DATABASE 'x' AS y", 50, confirmed=True)
    assert exc.value.kind == "changes-state"
    assert "cannot be confirmed" in str(exc.value)


def test_stacked_statements_cannot_be_confirmed(conn):
    with pytest.raises(safe_sql.UnsafeQuery):
        safe_sql.run(conn, "SELECT 1; DROP TABLE SPORTS", 50, confirmed=True)
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7


def test_presets_still_go_through_the_read_only_check():
    with pytest.raises(safe_sql.UnsafeQuery):
        safe_sql.validate("DELETE FROM SPORTS")


# ------------------------------------------------------------------ web flow


def test_console_asks_before_running_a_write(client, conn):
    body = client.post(
        "/query", data={"sql": "DELETE FROM SPORTS WHERE Sport_ID = 7"}
    ).get_data(as_text=True)
    assert "this will change the database" in body.lower()
    assert "Yes, run this DELETE" in body
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7


def test_console_runs_the_write_once_confirmed(client, conn):
    body = client.post(
        "/query",
        data={"sql": "DELETE FROM SPORTS WHERE Sport_ID = 7", "confirm": "yes"},
    ).get_data(as_text=True)
    assert "1 row changed" in body
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 6


@pytest.mark.parametrize(
    "path", ["/students", "/staff", "/sports", "/challenges", "/equipment"]
)
def test_paged_pages_render(client, path):
    assert client.get(f"{path}?page=2&per_page=10").status_code == 200
    assert client.get(f"{path}?page=abc&per_page=zzz").status_code == 200


def test_pager_links_carry_the_page_size(client):
    """12 seeded students at 10 per page is the smallest list that pages."""
    body = client.get("/students?per_page=10").get_data(as_text=True)
    assert "page=2&amp;per_page=10" in body
    assert "Showing 1-10 of 12" in body
    # The page-size choices come from a context processor, so the macro has to
    # be imported `with context` or they silently render as nothing.
    assert "per_page=25" in body
    assert "per_page=100" in body


def test_paging_keeps_the_filter(client, conn):
    for n in range(20, 32):
        conn.execute(
            "INSERT INTO FITNESS_CHALLENGES (Challenge_ID, Challenge_Name) "
            "VALUES (?, ?)",
            (n, f"Extra {n} Challenge"),
        )
    conn.commit()

    body = client.get("/challenges?q=Challenge&per_page=10").get_data(as_text=True)
    assert "q=Challenge" in body
    assert "of 18" in body
