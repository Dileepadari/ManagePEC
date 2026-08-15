"""Validation tests: the layer the phase-4 script did not have."""

from __future__ import annotations

from datetime import date

import pytest

from managepec.models import (
    ChallengeInput,
    StaffInput,
    StudentInput,
    ValidationError,
    parse_contact,
    parse_date,
    parse_day_code,
    parse_int,
    parse_text,
    parse_time,
    split_name,
)


def valid_student(**overrides):
    data = {
        "student_id": "50",
        "name": "Asha Rao",
        "date_of_birth": "2004-05-05",
        "contact": "+91-9800011155",
        "department": "CSE",
        "course_year": "2024",
        "credits_done": "0",
        "assigned_sport": "1",
        "attendance": "70",
    }
    data.update(overrides)
    return data


def valid_staff(**overrides):
    data = {
        "staff_id": "50",
        "name": "Ravi Kumar",
        "contact": "+91-9800011166",
        "join_date": "2023-01-01",
        "staff_type": "Trainer",
        "total_salary": "50000",
        "pending_salary": "1000",
        "sport_id": "1",
        "position": "Trainer",
        "supervisor": "1",
        "task_work": "",
        "task_day": "",
        "task_time": "",
    }
    data.update(overrides)
    return data


def valid_challenge(**overrides):
    data = {
        "challenge_id": "50",
        "challenge_name": "Sprint Challenge",
        "from_date": "2024-03-01",
        "to_date": "2024-03-31",
        "registration_deadline": "2024-02-15",
        "section_ref_id": "50",
        "section_name": "Heats",
        "section_date": "2024-03-05",
        "location": "Track",
        "mentor_id": "1",
        "winner_id": "1",
        "prize": "Medal",
    }
    data.update(overrides)
    return data


# ------------------------------------------------------------ field parsers


@pytest.mark.parametrize("value", ["", "   ", None, "twelve", "1.5"])
def test_parse_int_rejects_non_numbers(value):
    with pytest.raises(ValidationError):
        parse_int("age", value)


def test_parse_int_enforces_bounds():
    with pytest.raises(ValidationError):
        parse_int("attendance", "101", minimum=0, maximum=100)
    assert parse_int("attendance", " 100 ", minimum=0, maximum=100) == 100


def test_parse_date_accepts_iso_and_date_objects():
    assert parse_date("dob", "2004-01-02") == "2004-01-02"
    assert parse_date("dob", date(2004, 1, 2)) == "2004-01-02"


@pytest.mark.parametrize("value", ["02-01-2004", "2004/01/02", "not a date", ""])
def test_parse_date_rejects_other_formats(value):
    with pytest.raises(ValidationError):
        parse_date("dob", value)


def test_parse_time_normalises():
    assert parse_time("t", "06:30") == "06:30:00"
    assert parse_time("t", "06:30:15") == "06:30:15"


@pytest.mark.parametrize("value", ["+91-9800011155", "9800011155", "080 1234567"])
def test_parse_contact_accepts_reasonable_numbers(value):
    assert parse_contact("contact", value) == value


@pytest.mark.parametrize("value", ["12345", "not-a-number", "'; DROP TABLE SPORTS--"])
def test_parse_contact_rejects_junk(value):
    with pytest.raises(ValidationError):
        parse_contact("contact", value)


def test_split_name_requires_two_parts():
    assert split_name("name", "Asha Rao") == ("Asha", "Rao")
    assert split_name("name", "Asha Kumari Rao") == ("Asha", "Rao")
    with pytest.raises(ValidationError):
        split_name("name", "Asha")


def test_parse_day_code_normalises_case():
    assert parse_day_code("day", "mwf") == "MWF"
    with pytest.raises(ValidationError):
        parse_day_code("day", "MONDAY")


def test_parse_text_enforces_length():
    with pytest.raises(ValidationError):
        parse_text("department", "x" * 51, max_length=50)


# ------------------------------------------------------------------ payloads


def test_student_input_accepts_a_good_record():
    student = StudentInput.from_raw(valid_student())
    assert student.first_name == "Asha"
    assert student.last_name == "Rao"
    assert student.assigned_sport == 1


def test_student_input_allows_no_sport():
    student = StudentInput.from_raw(valid_student(assigned_sport=""))
    assert student.assigned_sport is None


def test_student_input_rejects_out_of_range_attendance():
    with pytest.raises(ValidationError) as exc:
        StudentInput.from_raw(valid_student(attendance="150"))
    assert exc.value.field == "attendance"


def test_staff_input_rejects_self_supervision():
    with pytest.raises(ValidationError) as exc:
        StaffInput.from_raw(valid_staff(supervisor="50"))
    assert exc.value.field == "supervisor"


def test_staff_input_task_fields_are_all_or_nothing():
    staff = StaffInput.from_raw(valid_staff())
    assert staff.task_work is None

    with_task = StaffInput.from_raw(
        valid_staff(task_work="Drills", task_day="2024-01-01", task_time="07:00")
    )
    assert with_task.task_time == "07:00:00"

    with pytest.raises(ValidationError):
        StaffInput.from_raw(valid_staff(task_work="Drills", task_day="", task_time=""))


def test_challenge_input_rejects_end_before_start():
    with pytest.raises(ValidationError) as exc:
        ChallengeInput.from_raw(
            valid_challenge(from_date="2024-03-31", to_date="2024-03-01")
        )
    assert exc.value.field == "to_date"


def test_challenge_input_rejects_deadline_after_start():
    with pytest.raises(ValidationError) as exc:
        ChallengeInput.from_raw(valid_challenge(registration_deadline="2024-03-15"))
    assert exc.value.field == "from_date"


def test_challenge_input_requires_a_prize_with_a_winner():
    with pytest.raises(ValidationError) as exc:
        ChallengeInput.from_raw(valid_challenge(prize=""))
    assert exc.value.field == "prize"


def test_challenge_input_drops_prize_without_a_winner():
    challenge = ChallengeInput.from_raw(valid_challenge(winner_id="", prize="Medal"))
    assert challenge.winner_id is None
    assert challenge.prize is None
