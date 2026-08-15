"""Repository tests, including the specific bugs carried over from phase 4."""

from __future__ import annotations

import pytest

from managepec import repository as repo
from managepec.models import ChallengeInput, StaffInput, StudentInput
from tests.test_models import valid_challenge, valid_staff, valid_student


# --------------------------------------------------------------------- create


def test_add_student_writes_all_three_tables(conn):
    repo.add_student(conn, StudentInput.from_raw(valid_student()))
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 50"
    ) == 1
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_ACAD_DETAILS WHERE Student_ID = 50"
    ) == 1
    assert conn.scalar(
        "SELECT Attendance FROM STUDENT_SPORT_DETAILS WHERE Student_ID = 50"
    ) == 70


def test_add_student_bumps_the_participant_count(conn):
    before = conn.scalar("SELECT No_of_Participants FROM SPORTS WHERE Sport_ID = 1")
    repo.add_student(conn, StudentInput.from_raw(valid_student()))
    after = conn.scalar("SELECT No_of_Participants FROM SPORTS WHERE Sport_ID = 1")
    assert after == before + 1


def test_add_student_rejects_a_duplicate_id(conn):
    with pytest.raises(repo.DuplicateRecord):
        repo.add_student(conn, StudentInput.from_raw(valid_student(student_id="1")))


def test_add_student_rejects_an_unknown_sport(conn):
    with pytest.raises(repo.NotFound):
        repo.add_student(conn, StudentInput.from_raw(valid_student(assigned_sport="99")))


def test_add_student_refuses_to_overfill_a_sport(conn):
    conn.execute(
        "UPDATE SPORTS SET Capacity = 5, No_of_Participants = 5 WHERE Sport_ID = 1"
    )
    conn.commit()
    with pytest.raises(repo.CapacityExceeded):
        repo.add_student(conn, StudentInput.from_raw(valid_student()))


def test_failed_student_insert_leaves_nothing_behind(conn):
    # Student 1 already exists in the seed, so the second table insert must fail
    # and the first must not survive it.
    payload = valid_student(student_id="60")
    repo.add_student(conn, StudentInput.from_raw(payload))
    with pytest.raises(repo.DuplicateRecord):
        repo.add_student(conn, StudentInput.from_raw(payload))
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 60"
    ) == 1


def test_add_staff_writes_position_and_optional_task(conn):
    repo.add_staff(
        conn,
        StaffInput.from_raw(
            valid_staff(task_work="Drills", task_day="2024-01-01", task_time="07:00")
        ),
    )
    assert conn.scalar("SELECT COUNT(*) FROM STAFF_POSITION WHERE Staff_ID = 50") == 1
    assert conn.scalar(
        "SELECT Work FROM STAFF_TASKS WHERE Staff_ID = 50"
    ) == "Drills"


def test_add_staff_rejects_pending_above_total(conn):
    with pytest.raises(repo.RepositoryError):
        repo.add_staff(
            conn,
            StaffInput.from_raw(valid_staff(total_salary="1000", pending_salary="2000")),
        )


def test_add_staff_rejects_unknown_supervisor(conn):
    with pytest.raises(repo.NotFound):
        repo.add_staff(conn, StaffInput.from_raw(valid_staff(supervisor="900")))


def test_add_challenge_writes_every_related_row(conn):
    repo.add_fitness_challenge(conn, ChallengeInput.from_raw(valid_challenge()))
    assert conn.scalar(
        "SELECT COUNT(*) FROM FITNESS_CHALLENGES_DETAILS WHERE Challenge_ID = 50"
    ) == 1
    assert conn.scalar(
        "SELECT COUNT(*) FROM FITNESS_SECTIONS_DETAILS WHERE CS_REF_ID = 50"
    ) == 1
    assert conn.scalar(
        "SELECT COUNT(*) FROM FITNESS_CHALLENGE_MENTORS WHERE CS_REF_ID = 50"
    ) == 1
    assert conn.scalar(
        "SELECT Prize FROM FITNESS_CHALLENGE_WINNERS WHERE CS_REF_ID = 50"
    ) == "Medal"


def test_add_challenge_rejects_a_reused_section_ref(conn):
    with pytest.raises(repo.DuplicateRecord):
        repo.add_fitness_challenge(
            conn, ChallengeInput.from_raw(valid_challenge(section_ref_id="1"))
        )


# --------------------------------------------------------------------- delete


def test_remove_sport_keeps_students_and_clears_the_reference(conn):
    """The phase-4 bug: ON DELETE CASCADE removed the student rows outright."""
    enrolled = [
        row["Student_ID"] for row in repo.students_in_sport(conn, 1)
    ]
    assert enrolled

    repo.remove_sport(conn, 1)

    for student_id in enrolled:
        assert conn.scalar(
            "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = ?",
            (student_id,),
        ) == 1
        assert conn.scalar(
            "SELECT Assigned_Sport FROM STUDENT_SPORT_DETAILS WHERE Student_ID = ?",
            (student_id,),
        ) is None


def test_remove_sport_keeps_staff_and_equipment(conn):
    repo.remove_sport(conn, 1)
    assert conn.scalar("SELECT COUNT(*) FROM STAFF_DETAILS WHERE Staff_ID = 1") == 1
    assert conn.scalar(
        "SELECT Sport_ID FROM STAFF_POSITION WHERE Staff_ID = 1"
    ) is None
    assert conn.scalar(
        "SELECT Sport_ID FROM EQUIPMENT WHERE Equipment_ID = 1"
    ) is None


def test_remove_sport_cascades_slots_and_location(conn):
    repo.remove_sport(conn, 1)
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS_SLOT WHERE Sport_ID = 1") == 0
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS_LOCATION WHERE Sport_ID = 1") == 0


def test_remove_sport_rejects_an_unknown_id(conn):
    with pytest.raises(repo.NotFound):
        repo.remove_sport(conn, 999)


def test_remove_equipment_clears_the_funding_link(conn):
    """The phase-4 script used `UPDATE FROM ...`, which is not valid SQL."""
    repo.remove_equipment(conn, 1)
    assert conn.scalar("SELECT COUNT(*) FROM EQUIPMENT WHERE Equipment_ID = 1") == 0
    assert conn.scalar(
        "SELECT COUNT(*) FROM EQUIPMENT_MAINTENANCE WHERE Equipment_ID = 1"
    ) == 0
    assert conn.scalar("SELECT COUNT(*) FROM EQUIPMENT_FUNDS WHERE Transaction_ID = 1") == 1
    assert conn.scalar(
        "SELECT Equipment_ID FROM EQUIPMENT_FUNDS WHERE Transaction_ID = 1"
    ) is None


# --------------------------------------------------------------------- update


def test_update_student_changes_only_what_was_given(conn):
    repo.update_student(conn, 1, contact="+91-9999999999")
    assert conn.scalar(
        "SELECT Contact FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 1"
    ) == "+91-9999999999"
    assert conn.scalar(
        "SELECT Attendance FROM STUDENT_SPORT_DETAILS WHERE Student_ID = 1"
    ) == 90


def test_update_student_reports_a_missing_student(conn):
    """Phase 4 printed 'updated' for IDs that did not exist."""
    with pytest.raises(repo.NotFound):
        repo.update_student(conn, 999, contact="+91-9999999999")


def test_update_student_rejects_an_empty_update(conn):
    with pytest.raises(repo.RepositoryError):
        repo.update_student(conn, 1)


def test_update_staff_refuses_pending_above_total(conn):
    with pytest.raises(repo.RepositoryError):
        repo.update_staff(conn, 1, pending_salary=10**9)


def test_update_staff_keeps_the_untouched_figure(conn):
    repo.update_staff(conn, 1, total_salary=80000)
    row = conn.query_one(
        "SELECT Total_Salary, Pending_Salary FROM STAFF_PROFESSIONAL WHERE Staff_ID = 1"
    )
    assert row["Total_Salary"] == 80000
    assert row["Pending_Salary"] == 20000


def test_update_challenge_moves_the_venue(conn):
    repo.update_fitness_challenge(conn, 1, location="New Ground")
    assert conn.scalar(
        "SELECT Location FROM FITNESS_SECTIONS_DETAILS WHERE CS_REF_ID = 1"
    ) == "New Ground"


def test_update_challenge_reports_a_missing_section(conn):
    with pytest.raises(repo.NotFound):
        repo.update_fitness_challenge(conn, 999, location="Nowhere")


# ----------------------------------------------------------------------- read


def test_students_in_sport_lists_the_roster(conn):
    rows = repo.students_in_sport(conn, 1)
    assert {row["Student_ID"] for row in rows} == {1, 6, 7}


def test_students_in_sport_rejects_an_unknown_sport(conn):
    with pytest.raises(repo.NotFound):
        repo.students_in_sport(conn, 999)


def test_staff_in_sport_lists_the_posts(conn):
    rows = repo.staff_in_sport(conn, 1)
    assert [row["Staff_ID"] for row in rows] == [1]


def test_sports_on_day_groups_by_slot(conn):
    rows = repo.sports_on_day(conn, "MWF")
    assert rows
    assert all(row["Booked"] >= 1 for row in rows)


def test_sports_on_day_is_empty_for_an_unused_code(conn):
    assert repo.sports_on_day(conn, "SUN") == []


def test_equipment_on_date(conn):
    rows = repo.equipment_on_date(conn, "2023-02-20")
    assert {row["Equipment_ID"] for row in rows} == {5, 6}


def test_search_sport_by_name_is_exact(conn):
    assert len(repo.search_sport_by_name(conn, "Football")) == 1
    assert repo.search_sport_by_name(conn, "foot") == []


def test_search_sport_by_name_is_not_injectable(conn):
    """The value is bound, so this is looked up as a literal name."""
    rows = repo.search_sport_by_name(conn, "x' OR '1'='1")
    assert rows == []
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7


def test_search_challenges_matches_a_fragment(conn):
    rows = repo.search_challenges(conn, "Challenge")
    assert len(rows) == 6


def test_search_challenges_treats_wildcards_as_text(conn):
    """A bare % must not turn into 'match everything'."""
    assert repo.search_challenges(conn, "%") == []


# ------------------------------------------------------------------ aggregate


def test_funds_released_in_month(conn):
    february = repo.funds_released_in_month(conn, 2)
    assert february["releases"] == 2
    assert february["total"] == 7000 + 3000


def test_funds_released_in_an_empty_month_returns_zero(conn):
    assert repo.funds_released_in_month(conn, 12) == {
        "month": 12,
        "total": 0,
        "releases": 0,
    }


def test_funds_released_rejects_a_bad_month(conn):
    with pytest.raises(repo.RepositoryError):
        repo.funds_released_in_month(conn, 13)


def test_total_pending_salary(conn):
    assert repo.total_pending_salary(conn) == 20000 + 18000 + 22000 + 25000 + 28000 + 0 + 12000 + 5000


def test_average_students_per_sport_counts_empty_sports(conn):
    # 11 enrolled students spread over 7 sports.
    assert repo.average_students_per_sport(conn) == pytest.approx(11 / 7, abs=0.01)


# ----------------------------------------------------------------- dashboards


def test_summary_counts(conn):
    counts = repo.summary_counts(conn)
    assert counts["students"] == 12
    assert counts["staff"] == 8
    assert counts["sports"] == 7
    assert counts["challenges"] == 6


def test_sport_enrolment_includes_sports_with_nobody(conn):
    rows = repo.sport_enrolment(conn)
    by_name = {row["Sport_Name"]: row["Enrolled"] for row in rows}
    assert by_name["Table Tennis"] == 0
    assert by_name["Football"] == 3


def test_unassigned_students(conn):
    assert [row["Student_ID"] for row in repo.unassigned_students(conn)] == [12]


def test_equipment_status_uses_the_latest_check(conn):
    rows = {row["Equipment_ID"]: row for row in repo.equipment_status(conn)}
    assert rows[1]["Status"] == "Under Maintenance"
    assert str(rows[1]["Date"]) == "2023-06-01"


def test_attendance_by_department_is_sorted(conn):
    rows = repo.attendance_by_department(conn)
    values = [row["AvgAttendance"] for row in rows]
    assert values == sorted(values, reverse=True)


def test_funds_by_month_covers_every_month_with_a_release(conn):
    months = [row["Month"] for row in repo.funds_by_month(conn)]
    assert months == [1, 2, 3, 4, 5]


def test_listings_return_rows(conn):
    assert len(repo.list_students(conn)) == 12
    assert len(repo.list_staff(conn)) == 8
    assert len(repo.list_sports(conn)) == 7
    assert len(repo.list_challenges(conn)) == 6
