"""Route tests against a real Flask test client."""

from __future__ import annotations

import pytest

pytest.importorskip("flask")


@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/students",
        "/staff",
        "/sports",
        "/challenges",
        "/equipment",
        "/saved-queries",
        "/query",
        "/analysis",
    ],
)
def test_every_page_renders(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b"ManagePEC" in response.data


def test_unknown_page_returns_the_styled_404(client):
    """A blueprint-scoped errorhandler would miss this and leak Flask's own page."""
    response = client.get("/nope")
    assert response.status_code == 404
    body = response.get_data(as_text=True)
    assert "Page not found." in body
    assert "Back to the dashboard" in body


def test_dashboard_shows_the_headline_numbers(client):
    body = client.get("/").get_data(as_text=True)
    assert "Students" in body
    assert "Students without a sport" in body


def test_api_summary_is_json(client):
    payload = client.get("/api/summary").get_json()
    assert payload["counts"]["sports"] == 7
    assert payload["average_students_per_sport"] > 0
    assert len(payload["enrolment"]) == 7


# ------------------------------------------------------------------- students


def test_add_student_via_the_form(client, conn):
    response = client.post(
        "/students",
        data={
            "student_id": "70",
            "name": "Nina Shah",
            "date_of_birth": "2005-01-01",
            "contact": "+91-9800012345",
            "department": "CSE",
            "course_year": "2024",
            "credits_done": "0",
            "assigned_sport": "1",
            "attendance": "60",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Student added." in response.get_data(as_text=True)
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 70"
    ) == 1


def test_add_student_with_a_bad_date_shows_the_error(client, conn):
    response = client.post(
        "/students",
        data={
            "student_id": "71",
            "name": "Nina Shah",
            "date_of_birth": "01/01/2005",
            "contact": "+91-9800012345",
            "department": "CSE",
            "course_year": "2024",
            "credits_done": "0",
            "assigned_sport": "",
            "attendance": "60",
        },
    )
    assert "date_of_birth" in response.get_data(as_text=True)
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 71"
    ) == 0


def test_update_student_contact(client, conn):
    client.post(
        "/students/1/update", data={"contact": "+91-9000000000"}, follow_redirects=True
    )
    assert conn.scalar(
        "SELECT Contact FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 1"
    ) == "+91-9000000000"


# ---------------------------------------------------------------------- staff


def test_add_staff_via_the_form(client, conn):
    response = client.post(
        "/staff",
        data={
            "staff_id": "70",
            "name": "Arun Das",
            "contact": "+91-9800054321",
            "join_date": "2024-01-01",
            "staff_type": "Trainer",
            "position": "Trainer",
            "total_salary": "45000",
            "pending_salary": "0",
            "sport_id": "2",
            "supervisor": "1",
            "task_work": "",
            "task_day": "",
            "task_time": "",
        },
        follow_redirects=True,
    )
    assert "Staff member added." in response.get_data(as_text=True)
    assert conn.scalar("SELECT COUNT(*) FROM STAFF_DETAILS WHERE Staff_ID = 70") == 1


# --------------------------------------------------------------------- sports


def test_retire_sport_keeps_the_students(client, conn):
    response = client.post("/sports/1/retire", follow_redirects=True)
    assert "Retired Football" in response.get_data(as_text=True)
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS WHERE Sport_ID = 1") == 0
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 1"
    ) == 1


def test_retire_an_unknown_sport_flashes_an_error(client):
    response = client.post("/sports/999/retire", follow_redirects=True)
    assert "no sport with ID 999" in response.get_data(as_text=True)


def test_sports_day_filter(client):
    body = client.get("/sports?day=mwf").get_data(as_text=True)
    assert "Football" in body


# ------------------------------------------------------------------ equipment


def test_retire_equipment(client, conn):
    client.post("/equipment/1/retire", follow_redirects=True)
    assert conn.scalar("SELECT COUNT(*) FROM EQUIPMENT WHERE Equipment_ID = 1") == 0


def test_equipment_date_filter(client):
    body = client.get("/equipment?date=2023-02-20").get_data(as_text=True)
    assert "Badminton Shuttlecocks" in body


# ----------------------------------------------------------------- challenges


def test_challenge_search(client):
    body = client.get("/challenges?q=Yoga").get_data(as_text=True)
    assert "Yoga Challenge" in body
    assert "Cardio Challenge" not in body


def test_add_challenge_with_a_deadline_after_the_start_is_refused(client, conn):
    response = client.post(
        "/challenges",
        data={
            "challenge_id": "70",
            "challenge_name": "Bad Challenge",
            "from_date": "2024-03-01",
            "to_date": "2024-03-31",
            "registration_deadline": "2024-03-15",
            "section_ref_id": "70",
            "section_name": "Heats",
            "section_date": "2024-03-05",
            "location": "Track",
            "mentor_id": "",
            "winner_id": "",
            "prize": "",
        },
    )
    assert "from_date" in response.get_data(as_text=True)
    assert conn.scalar(
        "SELECT COUNT(*) FROM FITNESS_CHALLENGES WHERE Challenge_ID = 70"
    ) == 0


# -------------------------------------------------------------- query console


def test_query_console_runs_a_select(client):
    body = client.post(
        "/query", data={"sql": "SELECT Sport_Name FROM SPORTS ORDER BY Sport_ID"}
    ).get_data(as_text=True)
    assert "Football" in body


def test_query_console_warns_that_a_delete_would_change_the_database(client, conn):
    body = client.post("/query", data={"sql": "DELETE FROM SPORTS"}).get_data(
        as_text=True
    )
    assert "this would have changed the database" in body
    assert "would change data in the database (DELETE)" in body
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7


def test_query_console_warns_about_ddl(client, conn):
    body = client.post("/query", data={"sql": "DROP TABLE SPORTS"}).get_data(
        as_text=True
    )
    assert "this would have changed the database" in body
    assert "would change the database schema (DROP)" in body
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7


def test_query_console_does_not_shout_about_a_plain_syntax_refusal(client):
    body = client.post("/query", data={"sql": "EXPLAIN SELECT 1"}).get_data(
        as_text=True
    )
    assert "this would have changed the database" not in body
    assert "Only SELECT and WITH queries can run here." in body


def test_query_console_reports_a_sql_error(client):
    body = client.post("/query", data={"sql": "SELECT * FROM NOPE"}).get_data(
        as_text=True
    )
    assert "rejected that query" in body


def test_query_console_caps_rows(app, client):
    app.config["MAX_QUERY_ROWS"] = 2
    body = client.post(
        "/query", data={"sql": "SELECT * FROM STUDENT_PERSONAL_DETAILS"}
    ).get_data(as_text=True)
    assert "cut off at 2 rows" in body


# -------------------------------------------------------------- saved queries


def test_saved_queries_default_to_the_first_preset(client):
    body = client.get("/saved-queries").get_data(as_text=True)
    assert "Roster for every sport" in body


@pytest.mark.parametrize(
    "key",
    [
        "roster",
        "capacity",
        "attendance",
        "pending_salary",
        "funds",
        "maintenance",
        "winners",
        "supervision",
        "medical",
        "unassigned",
    ],
)
def test_every_saved_query_runs(client, key):
    response = client.get(f"/saved-queries?key={key}")
    assert response.status_code == 200
    assert "Traceback" not in response.get_data(as_text=True)


def test_unknown_preset_key_falls_back(client):
    assert client.get("/saved-queries?key=nope").status_code == 200


# ------------------------------------------------------------------- analysis


def test_analysis_month_filter(client):
    body = client.get("/analysis?month=2").get_data(as_text=True)
    assert "Month 2" in body


def test_analysis_rejects_a_bad_month(client):
    response = client.get("/analysis?month=13")
    assert response.status_code == 200
    assert "month must be between 1 and 12" in response.get_data(as_text=True)
