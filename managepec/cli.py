"""Terminal front end for ManagePEC.

This replaces the phase-4 `pec.py`.  The menu offers the same seventeen
operations, but each one now validates its input, runs parameterised SQL through
`repository`, and reports what actually happened instead of printing the SQL it
was about to run.

    python -m managepec.cli init-db      create the tables and load sample data
    python -m managepec.cli menu         the interactive menu (also the default)
    python -m managepec.cli list students
    python -m managepec.cli report
"""

from __future__ import annotations

import argparse
import sys
from typing import Callable, Sequence

from .config import load_settings
from .db import Connection, Database, DatabaseError, Row
from .models import (
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
from . import repository as repo

MENU = [
    ("Add a student", "add_student"),
    ("Add a staff member", "add_staff"),
    ("Add a fitness challenge", "add_challenge"),
    ("Retire a sport", "remove_sport"),
    ("Retire a piece of equipment", "remove_equipment"),
    ("Update student details", "update_student"),
    ("Update staff details", "update_staff"),
    ("Update a fitness challenge", "update_challenge"),
    ("List students in a sport", "students_in_sport"),
    ("List staff in a sport", "staff_in_sport"),
    ("Sports running on a day", "sports_on_day"),
    ("Equipment serviced on a date", "equipment_on_date"),
    ("Funds released in a month", "funds_in_month"),
    ("Total pending salary", "pending_salary"),
    ("Look up a sport by name", "search_sport"),
    ("Search challenges by name", "search_challenges"),
    ("Average students per sport", "average_students"),
    ("Overview report", "report"),
]


# ------------------------------------------------------------------ rendering


def format_table(rows: Sequence[Row], empty: str = "No rows.") -> str:
    """Render a list of dict rows as a fixed-width table."""
    if not rows:
        return empty
    columns = list(rows[0].keys())
    widths = {
        col: max(len(col), *(len(_cell(row.get(col))) for row in rows))
        for col in columns
    }
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    rule = "  ".join("-" * widths[col] for col in columns)
    body = [
        "  ".join(_cell(row.get(col)).ljust(widths[col]) for col in columns)
        for row in rows
    ]
    return "\n".join([header, rule, *body, "", f"{len(rows)} row(s)"])


def _cell(value: object) -> str:
    if value is None:
        return "-"
    return str(value)


def show(rows: Sequence[Row], empty: str = "No rows.") -> None:
    print(format_table(rows, empty))


# --------------------------------------------------------------------- prompts


def ask(label: str, *, allow_blank: bool = False) -> str:
    while True:
        try:
            value = input(f"{label}: ").strip()
        except EOFError:
            raise KeyboardInterrupt from None
        if value or allow_blank:
            return value
        print("  this field is required")


def ask_optional(label: str) -> str | None:
    value = ask(f"{label} (blank to skip)", allow_blank=True)
    return value or None


def ask_field(
    label: str,
    field: str,
    parser: Callable[..., object],
    *,
    optional: bool = False,
    **kwargs: object,
) -> str | None:
    """Prompt until the answer passes `parser`, then return the raw text.

    The payload dataclasses parse the whole record again, so validation still
    lives in one place; checking here as well just means the user is told about
    a bad date on the line they typed it, not after nine more prompts.
    """
    while True:
        raw = ask(label, allow_blank=optional) if not optional else ask(
            f"{label} (blank to skip)", allow_blank=True
        )
        if optional and not raw:
            return None
        try:
            parser(field, raw, **kwargs)
        except ValidationError as exc:
            print(f"  {exc.message}")
            continue
        return raw


def ask_yes_no(label: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = ask(f"{label} ({suffix})", allow_blank=True).lower()
    if not value:
        return default
    return value in {"y", "yes"}


# ------------------------------------------------------------------- handlers


def handle_add_student(conn: Connection) -> None:
    student = StudentInput.from_raw(
        {
            "student_id": ask_field("Student ID", "student_id", parse_int, minimum=1),
            "name": ask_field("Name (First Last)", "name", split_name),
            "date_of_birth": ask_field(
                "Date of birth (YYYY-MM-DD)", "date_of_birth", parse_date
            ),
            "contact": ask_field("Contact", "contact", parse_contact),
            "department": ask_field(
                "Department", "department", parse_text, max_length=50
            ),
            "course_year": ask_field(
                "Course year", "course_year", parse_text, max_length=50
            ),
            "credits_done": ask_field(
                "Credits done", "credits_done", parse_int, minimum=0
            ),
            "assigned_sport": ask_field(
                "Assigned sport ID", "assigned_sport", parse_int,
                optional=True, minimum=1,
            ),
            "attendance": ask_field(
                "Attendance (0-100)", "attendance", parse_int, minimum=0, maximum=100
            ),
        }
    )
    repo.add_student(conn, student)
    print(
        f"Added student {student.student_id} "
        f"({student.first_name} {student.last_name})."
    )


def handle_add_staff(conn: Connection) -> None:
    staff = StaffInput.from_raw(
        {
            "staff_id": ask_field("Staff ID", "staff_id", parse_int, minimum=1),
            "name": ask_field("Name (First Last)", "name", split_name),
            "contact": ask_field("Contact", "contact", parse_contact),
            "join_date": ask_field("Join date (YYYY-MM-DD)", "join_date", parse_date),
            "staff_type": ask_field(
                "Type (Coach, Trainer, ...)", "staff_type", parse_text, max_length=50
            ),
            "total_salary": ask_field(
                "Total salary", "total_salary", parse_int, minimum=0
            ),
            "pending_salary": ask_field(
                "Pending salary", "pending_salary", parse_int, minimum=0
            ),
            "sport_id": ask_field(
                "Sport ID", "sport_id", parse_int, optional=True, minimum=1
            ),
            "position": ask_field("Position", "position", parse_text, max_length=50),
            "supervisor": ask_field(
                "Supervisor staff ID", "supervisor", parse_int, optional=True, minimum=1
            ),
            "task_work": ask_field(
                "First task description", "task_work", parse_text,
                optional=True, max_length=100,
            ),
            "task_day": ask_field(
                "Task date (YYYY-MM-DD)", "task_day", parse_date, optional=True
            ),
            "task_time": ask_field(
                "Task time (HH:MM)", "task_time", parse_time, optional=True
            ),
        }
    )
    repo.add_staff(conn, staff)
    print(
        f"Added staff member {staff.staff_id} "
        f"({staff.first_name} {staff.last_name})."
    )


def handle_add_challenge(conn: Connection) -> None:
    challenge = ChallengeInput.from_raw(
        {
            "challenge_id": ask_field(
                "Challenge ID", "challenge_id", parse_int, minimum=1
            ),
            "challenge_name": ask_field(
                "Challenge name", "challenge_name", parse_text, max_length=50
            ),
            "registration_deadline": ask_field(
                "Registration deadline (YYYY-MM-DD)",
                "registration_deadline",
                parse_date,
            ),
            "from_date": ask_field("From date (YYYY-MM-DD)", "from_date", parse_date),
            "to_date": ask_field("To date (YYYY-MM-DD)", "to_date", parse_date),
            "section_ref_id": ask_field(
                "Section reference ID", "section_ref_id", parse_int, minimum=1
            ),
            "section_name": ask_field(
                "Section name", "section_name", parse_text, max_length=50
            ),
            "section_date": ask_field(
                "Section date (YYYY-MM-DD)", "section_date", parse_date
            ),
            "location": ask_field("Location", "location", parse_text, max_length=50),
            "mentor_id": ask_field(
                "Mentor staff ID", "mentor_id", parse_int, optional=True, minimum=1
            ),
            "winner_id": ask_field(
                "Winner student ID", "winner_id", parse_int, optional=True, minimum=1
            ),
            "prize": ask_field(
                "Prize", "prize", parse_text, optional=True, max_length=50
            ),
        }
    )
    repo.add_fitness_challenge(conn, challenge)
    print(f"Added challenge {challenge.challenge_id} ({challenge.challenge_name}).")


def handle_remove_sport(conn: Connection) -> None:
    sport_id = parse_int("sport_id", ask("Sport ID"), minimum=1)
    sport = repo.get_sport(conn, sport_id)
    if not ask_yes_no(f"Retire {sport['Sport_Name']}?"):
        print("Cancelled.")
        return
    repo.remove_sport(conn, sport_id)
    print(
        f"Retired {sport['Sport_Name']}. Students, staff and equipment kept their "
        "records with the sport reference cleared."
    )


def handle_remove_equipment(conn: Connection) -> None:
    equipment_id = parse_int("equipment_id", ask("Equipment ID"), minimum=1)
    removed = repo.remove_equipment(conn, equipment_id)
    print(f"Removed equipment {equipment_id} ({removed['Equipment_Name']}).")


def handle_update_student(conn: Connection) -> None:
    student_id = parse_int("student_id", ask("Student ID"), minimum=1)
    contact = ask_optional("New contact")
    attendance = ask_optional("New attendance (0-100)")
    repo.update_student(
        conn,
        student_id,
        contact=None if contact is None else parse_contact("contact", contact),
        attendance=None
        if attendance is None
        else parse_int("attendance", attendance, minimum=0, maximum=100),
    )
    print(f"Updated student {student_id}.")


def handle_update_staff(conn: Connection) -> None:
    staff_id = parse_int("staff_id", ask("Staff ID"), minimum=1)
    contact = ask_optional("New contact")
    total = ask_optional("New total salary")
    pending = ask_optional("New pending salary")
    repo.update_staff(
        conn,
        staff_id,
        contact=None if contact is None else parse_contact("contact", contact),
        total_salary=None if total is None else parse_int("total_salary", total, minimum=0),
        pending_salary=None
        if pending is None
        else parse_int("pending_salary", pending, minimum=0),
    )
    print(f"Updated staff member {staff_id}.")


def handle_update_challenge(conn: Connection) -> None:
    section_id = parse_int("section_ref_id", ask("Section reference ID"), minimum=1)
    location = ask_optional("New location")
    prize = ask_optional("New prize")
    repo.update_fitness_challenge(
        conn,
        section_id,
        location=None if location is None else parse_text("location", location, max_length=50),
        prize=None if prize is None else parse_text("prize", prize, max_length=50),
    )
    print(f"Updated challenge section {section_id}.")


def handle_students_in_sport(conn: Connection) -> None:
    sport_id = parse_int("sport_id", ask("Sport ID"), minimum=1)
    show(repo.students_in_sport(conn, sport_id), "Nobody is enrolled in that sport.")


def handle_staff_in_sport(conn: Connection) -> None:
    sport_id = parse_int("sport_id", ask("Sport ID"), minimum=1)
    show(repo.staff_in_sport(conn, sport_id), "No staff are posted to that sport.")


def handle_sports_on_day(conn: Connection) -> None:
    day = parse_day_code("day", ask("Day code (MWF, TTS, SUN, ALL)"))
    show(repo.sports_on_day(conn, day), f"No sports have slots on {day}.")


def handle_equipment_on_date(conn: Connection) -> None:
    on_date = parse_date("date", ask("Date (YYYY-MM-DD)"))
    show(repo.equipment_on_date(conn, on_date), f"No equipment was serviced on {on_date}.")


def handle_funds_in_month(conn: Connection) -> None:
    month = parse_int("month", ask("Month (1-12)"), minimum=1, maximum=12)
    result = repo.funds_released_in_month(conn, month)
    print(
        f"Month {result['month']}: {result['releases']} release(s), "
        f"total {result['total']}."
    )


def handle_pending_salary(conn: Connection) -> None:
    print(f"Total pending salary: {repo.total_pending_salary(conn)}")


def handle_search_sport(conn: Connection) -> None:
    name = parse_text("sport_name", ask("Sport name"), max_length=50)
    show(repo.search_sport_by_name(conn, name), f"No sport named {name}.")


def handle_search_challenges(conn: Connection) -> None:
    fragment = ask("Part of the challenge name", allow_blank=True)
    show(repo.search_challenges(conn, fragment), "No challenge matched.")


def handle_average_students(conn: Connection) -> None:
    print(f"Average students per sport: {repo.average_students_per_sport(conn)}")


def handle_report(conn: Connection) -> None:
    counts = repo.summary_counts(conn)
    print("Overview")
    print("--------")
    for label, value in counts.items():
        print(f"  {label.replace('_', ' ').title():<16} {value}")
    print()
    print("Enrolment per sport")
    show(repo.sport_enrolment(conn))
    print()
    print("Attendance by department")
    show(repo.attendance_by_department(conn))
    print()
    print("Students without a sport")
    show(repo.unassigned_students(conn), "Every student is enrolled somewhere.")


HANDLERS: dict[str, Callable[[Connection], None]] = {
    "add_student": handle_add_student,
    "add_staff": handle_add_staff,
    "add_challenge": handle_add_challenge,
    "remove_sport": handle_remove_sport,
    "remove_equipment": handle_remove_equipment,
    "update_student": handle_update_student,
    "update_staff": handle_update_staff,
    "update_challenge": handle_update_challenge,
    "students_in_sport": handle_students_in_sport,
    "staff_in_sport": handle_staff_in_sport,
    "sports_on_day": handle_sports_on_day,
    "equipment_on_date": handle_equipment_on_date,
    "funds_in_month": handle_funds_in_month,
    "pending_salary": handle_pending_salary,
    "search_sport": handle_search_sport,
    "search_challenges": handle_search_challenges,
    "average_students": handle_average_students,
    "report": handle_report,
}


# ----------------------------------------------------------------------- menu


def print_menu() -> None:
    print()
    print("ManagePEC")
    print("=========")
    for index, (label, _) in enumerate(MENU, start=1):
        print(f"{index:>2}. {label}")
    print(f"{len(MENU) + 1:>2}. Exit")


def run_menu(conn: Connection) -> int:
    """Loop until the user picks Exit or interrupts."""
    exit_choice = len(MENU) + 1
    while True:
        print_menu()
        try:
            raw = input("Choice> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not raw:
            continue
        if not raw.isdigit():
            print("Enter the number of an option.")
            continue

        choice = int(raw)
        if choice == exit_choice:
            return 0
        if not 1 <= choice <= len(MENU):
            print(f"Pick a number between 1 and {exit_choice}.")
            continue

        handler = HANDLERS[MENU[choice - 1][1]]
        try:
            handler(conn)
        except (ValidationError, repo.RepositoryError) as exc:
            conn.rollback()
            print(f"Error: {exc}")
        except KeyboardInterrupt:
            conn.rollback()
            print("\nCancelled.")
        except Exception as exc:  # unexpected, but must not kill the session
            conn.rollback()
            print(f"Unexpected error: {exc}")


# ------------------------------------------------------------------ arguments


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="managepec",
        description="Manage the Physical Education Centre database.",
    )
    sub = parser.add_subparsers(dest="command")

    init = sub.add_parser("init-db", help="create the tables and load sample data")
    init.add_argument(
        "--no-seed", action="store_true", help="create empty tables only"
    )

    sub.add_parser("menu", help="interactive menu (default)")

    listing = sub.add_parser("list", help="print one of the main tables")
    listing.add_argument(
        "what", choices=["students", "staff", "sports", "challenges", "equipment"]
    )

    sub.add_parser("report", help="print the overview report")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings()
    database = Database(settings)

    try:
        conn = database.connect()
    except DatabaseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.command == "init-db":
            database.initialise(conn, with_seed=not args.no_seed)
            target = (
                settings.sqlite_path
                if settings.backend == "sqlite"
                else f"{settings.mysql_host}/{settings.mysql_database}"
            )
            print(
                f"Initialised {settings.backend} database at {target}"
                + ("" if args.no_seed else " with sample data")
            )
            return 0

        if args.command == "list":
            readers = {
                "students": repo.list_students,
                "staff": repo.list_staff,
                "sports": repo.list_sports,
                "challenges": repo.list_challenges,
                "equipment": repo.equipment_status,
            }
            show(readers[args.what](conn))
            return 0

        if args.command == "report":
            handle_report(conn)
            return 0

        return run_menu(conn)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
