"""Input records and the validation that guards them.

The phase-4 script fed raw `input()` straight into a formatted SQL string, so a
blank field or a mistyped date became either a crash or a bad row.  Everything
that reaches the repository now goes through one of these dataclasses first, and
both the CLI and the web forms share that check.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMATS = ("%H:%M:%S", "%H:%M")
CONTACT_RE = re.compile(r"^[+0-9][0-9 \-]{6,14}$")
DAY_CODES = {"MWF", "TTS", "SUN", "ALL"}


class ValidationError(ValueError):
    """A field the user supplied is missing, malformed or out of range."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


# --------------------------------------------------------------- field parsers


def parse_int(field: str, value: object, *, minimum: int | None = None,
              maximum: int | None = None) -> int:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(field, "is required")
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError(field, f"must be a whole number, got {value!r}") from None
    if minimum is not None and number < minimum:
        raise ValidationError(field, f"must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise ValidationError(field, f"must be at most {maximum}")
    return number


def parse_optional_int(field: str, value: object, **kwargs: object) -> int | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return parse_int(field, value, **kwargs)  # type: ignore[arg-type]


def parse_text(field: str, value: object, *, max_length: int) -> str:
    if value is None:
        raise ValidationError(field, "is required")
    text = str(value).strip()
    if not text:
        raise ValidationError(field, "is required")
    if len(text) > max_length:
        raise ValidationError(field, f"must be at most {max_length} characters")
    return text


def parse_date(field: str, value: object) -> str:
    """Accept a date or an ISO string, return the canonical YYYY-MM-DD form."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.strftime(DATE_FORMAT)
    if isinstance(value, datetime):
        return value.date().strftime(DATE_FORMAT)
    text = parse_text(field, value, max_length=10)
    try:
        return datetime.strptime(text, DATE_FORMAT).strftime(DATE_FORMAT)
    except ValueError:
        raise ValidationError(field, "must be a date in YYYY-MM-DD form") from None


def parse_time(field: str, value: object) -> str:
    if isinstance(value, time):
        return value.strftime("%H:%M:%S")
    text = parse_text(field, value, max_length=8)
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%H:%M:%S")
        except ValueError:
            continue
    raise ValidationError(field, "must be a time in HH:MM or HH:MM:SS form")


def parse_contact(field: str, value: object) -> str:
    text = parse_text(field, value, max_length=15)
    if not CONTACT_RE.match(text):
        raise ValidationError(
            field, "must be 7 to 15 characters of digits, spaces, - or a leading +"
        )
    return text


def split_name(field: str, value: object) -> tuple[str, str]:
    """Split 'First Last' into its two halves, both required."""
    text = parse_text(field, value, max_length=101)
    parts = [part for part in text.split() if part]
    if len(parts) < 2:
        raise ValidationError(field, "needs both a first and a last name")
    return parts[0][:50], parts[-1][:50]


def parse_day_code(field: str, value: object) -> str:
    text = parse_text(field, value, max_length=5).upper()
    if text not in DAY_CODES:
        raise ValidationError(field, f"must be one of {', '.join(sorted(DAY_CODES))}")
    return text


def require_order(earlier_field: str, earlier: str, later_field: str, later: str) -> None:
    if datetime.strptime(later, DATE_FORMAT) < datetime.strptime(earlier, DATE_FORMAT):
        raise ValidationError(later_field, f"must not be before {earlier_field}")


# ------------------------------------------------------------------- payloads


@dataclass(frozen=True)
class StudentInput:
    student_id: int
    first_name: str
    last_name: str
    date_of_birth: str
    contact: str
    department: str
    course_year: str
    credits_done: int
    assigned_sport: int | None
    attendance: int

    @classmethod
    def from_raw(cls, data: dict[str, object]) -> "StudentInput":
        first, last = split_name("name", data.get("name"))
        return cls(
            student_id=parse_int("student_id", data.get("student_id"), minimum=1),
            first_name=first,
            last_name=last,
            date_of_birth=parse_date("date_of_birth", data.get("date_of_birth")),
            contact=parse_contact("contact", data.get("contact")),
            department=parse_text("department", data.get("department"), max_length=50),
            course_year=parse_text("course_year", data.get("course_year"), max_length=50),
            credits_done=parse_int("credits_done", data.get("credits_done"), minimum=0),
            assigned_sport=parse_optional_int(
                "assigned_sport", data.get("assigned_sport"), minimum=1
            ),
            attendance=parse_int(
                "attendance", data.get("attendance"), minimum=0, maximum=100
            ),
        )


@dataclass(frozen=True)
class StaffInput:
    staff_id: int
    first_name: str
    last_name: str
    contact: str
    join_date: str
    staff_type: str
    total_salary: int
    pending_salary: int
    sport_id: int | None
    position: str
    supervisor: int | None
    task_day: str | None
    task_time: str | None
    task_work: str | None

    @classmethod
    def from_raw(cls, data: dict[str, object]) -> "StaffInput":
        first, last = split_name("name", data.get("name"))
        staff_id = parse_int("staff_id", data.get("staff_id"), minimum=1)
        supervisor = parse_optional_int("supervisor", data.get("supervisor"), minimum=1)
        if supervisor == staff_id:
            raise ValidationError("supervisor", "cannot be the staff member themselves")

        work = data.get("task_work")
        has_task = bool(work and str(work).strip())
        return cls(
            staff_id=staff_id,
            first_name=first,
            last_name=last,
            contact=parse_contact("contact", data.get("contact")),
            join_date=parse_date("join_date", data.get("join_date")),
            staff_type=parse_text("staff_type", data.get("staff_type"), max_length=50),
            total_salary=parse_int("total_salary", data.get("total_salary"), minimum=0),
            pending_salary=parse_int(
                "pending_salary", data.get("pending_salary"), minimum=0
            ),
            sport_id=parse_optional_int("sport_id", data.get("sport_id"), minimum=1),
            position=parse_text("position", data.get("position"), max_length=50),
            supervisor=supervisor,
            task_day=parse_date("task_day", data.get("task_day")) if has_task else None,
            task_time=parse_time("task_time", data.get("task_time")) if has_task else None,
            task_work=parse_text("task_work", work, max_length=100) if has_task else None,
        )


@dataclass(frozen=True)
class ChallengeInput:
    challenge_id: int
    challenge_name: str
    from_date: str
    to_date: str
    registration_deadline: str
    section_ref_id: int
    section_name: str
    section_date: str
    location: str
    mentor_id: int | None
    winner_id: int | None
    prize: str | None

    @classmethod
    def from_raw(cls, data: dict[str, object]) -> "ChallengeInput":
        from_date = parse_date("from_date", data.get("from_date"))
        to_date = parse_date("to_date", data.get("to_date"))
        deadline = parse_date(
            "registration_deadline", data.get("registration_deadline")
        )
        require_order("from_date", from_date, "to_date", to_date)
        require_order("registration_deadline", deadline, "from_date", from_date)

        winner_id = parse_optional_int("winner_id", data.get("winner_id"), minimum=1)
        prize = data.get("prize")
        if winner_id is not None:
            prize = parse_text("prize", prize, max_length=50)
        else:
            prize = None

        return cls(
            challenge_id=parse_int("challenge_id", data.get("challenge_id"), minimum=1),
            challenge_name=parse_text(
                "challenge_name", data.get("challenge_name"), max_length=50
            ),
            from_date=from_date,
            to_date=to_date,
            registration_deadline=deadline,
            section_ref_id=parse_int(
                "section_ref_id", data.get("section_ref_id"), minimum=1
            ),
            section_name=parse_text(
                "section_name", data.get("section_name"), max_length=50
            ),
            section_date=parse_date("section_date", data.get("section_date")),
            location=parse_text("location", data.get("location"), max_length=50),
            mentor_id=parse_optional_int("mentor_id", data.get("mentor_id"), minimum=1),
            winner_id=winner_id,
            prize=prize,
        )


__all__ = [
    "ChallengeInput",
    "StaffInput",
    "StudentInput",
    "ValidationError",
    "parse_contact",
    "parse_date",
    "parse_day_code",
    "parse_int",
    "parse_optional_int",
    "parse_text",
    "parse_time",
    "split_name",
]
