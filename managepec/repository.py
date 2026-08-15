"""Every read and write the application performs.

One rule holds throughout: SQL text is a constant in this file and all user
values travel as bound parameters.  Functions return data (or raise), they never
print, so the CLI and the web layer can both call them.
"""

from __future__ import annotations

from .db import Connection, Row, month_expr
from .models import ChallengeInput, StaffInput, StudentInput


class RepositoryError(RuntimeError):
    """Base class for the errors a caller is expected to show to a user."""


class NotFound(RepositoryError):
    pass


class DuplicateRecord(RepositoryError):
    pass


class CapacityExceeded(RepositoryError):
    pass


# ----------------------------------------------------------------- assertions


def _exists(conn: Connection, sql: str, params: tuple) -> bool:
    return conn.query_one(sql, params) is not None


def get_sport(conn: Connection, sport_id: int) -> Row:
    """Fetch a sport or raise NotFound."""
    row = conn.query_one("SELECT * FROM SPORTS WHERE Sport_ID = ?", (sport_id,))
    if row is None:
        raise NotFound(f"no sport with ID {sport_id}")
    return row


def _require_staff(conn: Connection, staff_id: int) -> Row:
    row = conn.query_one("SELECT * FROM STAFF_DETAILS WHERE Staff_ID = ?", (staff_id,))
    if row is None:
        raise NotFound(f"no staff member with ID {staff_id}")
    return row


def _require_student(conn: Connection, student_id: int) -> Row:
    row = conn.query_one(
        "SELECT * FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = ?", (student_id,)
    )
    if row is None:
        raise NotFound(f"no student with ID {student_id}")
    return row


# --------------------------------------------------------------------- create


def add_student(conn: Connection, student: StudentInput) -> None:
    """Insert a student across the three tables that describe one, atomically."""
    if _exists(
        conn,
        "SELECT 1 FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = ?",
        (student.student_id,),
    ):
        raise DuplicateRecord(f"student {student.student_id} already exists")

    if student.assigned_sport is not None:
        sport = get_sport(conn, student.assigned_sport)
        if sport["No_of_Participants"] >= sport["Capacity"]:
            raise CapacityExceeded(
                f"{sport['Sport_Name']} is full "
                f"({sport['No_of_Participants']}/{sport['Capacity']})"
            )

    with conn.transaction():
        conn.execute(
            "INSERT INTO STUDENT_PERSONAL_DETAILS "
            "(Student_ID, First_Name, Last_Name, Date_of_Birth, Contact) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                student.student_id,
                student.first_name,
                student.last_name,
                student.date_of_birth,
                student.contact,
            ),
        )
        conn.execute(
            "INSERT INTO STUDENT_ACAD_DETAILS "
            "(Student_ID, Department, Course_Year, Credits_Done) VALUES (?, ?, ?, ?)",
            (
                student.student_id,
                student.department,
                student.course_year,
                student.credits_done,
            ),
        )
        conn.execute(
            "INSERT INTO STUDENT_SPORT_DETAILS "
            "(Student_ID, Assigned_Sport, Attendance) VALUES (?, ?, ?)",
            (student.student_id, student.assigned_sport, student.attendance),
        )
        if student.assigned_sport is not None:
            conn.execute(
                "UPDATE SPORTS SET No_of_Participants = No_of_Participants + 1 "
                "WHERE Sport_ID = ?",
                (student.assigned_sport,),
            )


def add_staff(conn: Connection, staff: StaffInput) -> None:
    """Insert a staff member, their contract, their post and an optional task."""
    if _exists(
        conn, "SELECT 1 FROM STAFF_DETAILS WHERE Staff_ID = ?", (staff.staff_id,)
    ):
        raise DuplicateRecord(f"staff member {staff.staff_id} already exists")
    if staff.pending_salary > staff.total_salary:
        raise RepositoryError("pending salary cannot exceed the total salary")
    if staff.sport_id is not None:
        get_sport(conn, staff.sport_id)
    if staff.supervisor is not None:
        _require_staff(conn, staff.supervisor)

    with conn.transaction():
        conn.execute(
            "INSERT INTO STAFF_DETAILS (Staff_ID, First_Name, Last_Name, Contact) "
            "VALUES (?, ?, ?, ?)",
            (staff.staff_id, staff.first_name, staff.last_name, staff.contact),
        )
        conn.execute(
            "INSERT INTO STAFF_PROFESSIONAL "
            "(Staff_ID, Join_Date, Type, Total_Salary, Pending_Salary) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                staff.staff_id,
                staff.join_date,
                staff.staff_type,
                staff.total_salary,
                staff.pending_salary,
            ),
        )
        conn.execute(
            "INSERT INTO STAFF_POSITION (Staff_ID, Sport_ID, Position, Supervisor) "
            "VALUES (?, ?, ?, ?)",
            (staff.staff_id, staff.sport_id, staff.position, staff.supervisor),
        )
        if staff.task_work is not None:
            conn.execute(
                "INSERT INTO STAFF_TASKS (Staff_ID, Day, Time, Work) "
                "VALUES (?, ?, ?, ?)",
                (staff.staff_id, staff.task_day, staff.task_time, staff.task_work),
            )


def add_fitness_challenge(conn: Connection, challenge: ChallengeInput) -> None:
    """Insert a challenge, its dates, one section and that section's details."""
    if _exists(
        conn,
        "SELECT 1 FROM FITNESS_CHALLENGES WHERE Challenge_ID = ?",
        (challenge.challenge_id,),
    ):
        raise DuplicateRecord(f"challenge {challenge.challenge_id} already exists")
    if _exists(
        conn,
        "SELECT 1 FROM FITNESS_SECTIONS WHERE CS_REF_ID = ?",
        (challenge.section_ref_id,),
    ):
        raise DuplicateRecord(f"section {challenge.section_ref_id} already exists")
    if challenge.mentor_id is not None:
        _require_staff(conn, challenge.mentor_id)
    if challenge.winner_id is not None:
        _require_student(conn, challenge.winner_id)

    with conn.transaction():
        conn.execute(
            "INSERT INTO FITNESS_CHALLENGES (Challenge_ID, Challenge_Name) "
            "VALUES (?, ?)",
            (challenge.challenge_id, challenge.challenge_name),
        )
        conn.execute(
            "INSERT INTO FITNESS_CHALLENGES_DETAILS "
            "(Challenge_ID, From_Date, To_Date, Registration_Deadline) "
            "VALUES (?, ?, ?, ?)",
            (
                challenge.challenge_id,
                challenge.from_date,
                challenge.to_date,
                challenge.registration_deadline,
            ),
        )
        conn.execute(
            "INSERT INTO FITNESS_SECTIONS (CS_REF_ID, Challenge_ID, Section_Name) "
            "VALUES (?, ?, ?)",
            (
                challenge.section_ref_id,
                challenge.challenge_id,
                challenge.section_name,
            ),
        )
        conn.execute(
            "INSERT INTO FITNESS_SECTIONS_DETAILS (CS_REF_ID, Date, Location) "
            "VALUES (?, ?, ?)",
            (challenge.section_ref_id, challenge.section_date, challenge.location),
        )
        if challenge.mentor_id is not None:
            conn.execute(
                "INSERT INTO FITNESS_CHALLENGE_MENTORS (CS_REF_ID, Mentor_ID) "
                "VALUES (?, ?)",
                (challenge.section_ref_id, challenge.mentor_id),
            )
        if challenge.winner_id is not None:
            conn.execute(
                "INSERT INTO FITNESS_CHALLENGE_WINNERS (CS_REF_ID, Winner_ID, Prize) "
                "VALUES (?, ?, ?)",
                (challenge.section_ref_id, challenge.winner_id, challenge.prize),
            )


# --------------------------------------------------------------------- delete


def remove_sport(conn: Connection, sport_id: int) -> Row:
    """Retire a sport.

    The schema does the rest: location rows and slot bookings cascade away,
    while the student, staff and equipment rows that pointed at the sport keep
    their record and have the reference set to NULL.  The phase-4 script wrote
    those UPDATEs by hand after the DELETE had already cascaded them out of
    existence.
    """
    sport = get_sport(conn, sport_id)
    with conn.transaction():
        conn.execute("DELETE FROM SPORTS WHERE Sport_ID = ?", (sport_id,))
    return sport


def remove_equipment(conn: Connection, equipment_id: int) -> Row:
    """Retire a piece of equipment, keeping the funding record it was bought with."""
    row = conn.query_one(
        "SELECT * FROM EQUIPMENT WHERE Equipment_ID = ?", (equipment_id,)
    )
    if row is None:
        raise NotFound(f"no equipment with ID {equipment_id}")
    with conn.transaction():
        conn.execute("DELETE FROM EQUIPMENT WHERE Equipment_ID = ?", (equipment_id,))
    return row


# --------------------------------------------------------------------- update


def update_student(
    conn: Connection,
    student_id: int,
    contact: str | None = None,
    attendance: int | None = None,
) -> None:
    """Change a student's contact number, their attendance, or both."""
    _require_student(conn, student_id)
    if contact is None and attendance is None:
        raise RepositoryError("nothing to update")

    with conn.transaction():
        if contact is not None:
            conn.execute(
                "UPDATE STUDENT_PERSONAL_DETAILS SET Contact = ? WHERE Student_ID = ?",
                (contact, student_id),
            )
        if attendance is not None:
            changed = conn.execute(
                "UPDATE STUDENT_SPORT_DETAILS SET Attendance = ? WHERE Student_ID = ?",
                (attendance, student_id),
            )
            if changed == 0:
                conn.execute(
                    "INSERT INTO STUDENT_SPORT_DETAILS "
                    "(Student_ID, Assigned_Sport, Attendance) VALUES (?, NULL, ?)",
                    (student_id, attendance),
                )


def update_staff(
    conn: Connection,
    staff_id: int,
    contact: str | None = None,
    total_salary: int | None = None,
    pending_salary: int | None = None,
) -> None:
    """Change a staff member's contact number and/or salary figures."""
    _require_staff(conn, staff_id)
    if contact is None and total_salary is None and pending_salary is None:
        raise RepositoryError("nothing to update")

    current = conn.query_one(
        "SELECT Total_Salary, Pending_Salary FROM STAFF_PROFESSIONAL WHERE Staff_ID = ?",
        (staff_id,),
    )
    if current is None:
        raise NotFound(f"staff member {staff_id} has no professional record")

    new_total = current["Total_Salary"] if total_salary is None else total_salary
    new_pending = current["Pending_Salary"] if pending_salary is None else pending_salary
    if new_pending > new_total:
        raise RepositoryError("pending salary cannot exceed the total salary")

    with conn.transaction():
        if contact is not None:
            conn.execute(
                "UPDATE STAFF_DETAILS SET Contact = ? WHERE Staff_ID = ?",
                (contact, staff_id),
            )
        if total_salary is not None or pending_salary is not None:
            conn.execute(
                "UPDATE STAFF_PROFESSIONAL SET Total_Salary = ?, Pending_Salary = ? "
                "WHERE Staff_ID = ?",
                (new_total, new_pending, staff_id),
            )


def update_fitness_challenge(
    conn: Connection,
    section_ref_id: int,
    location: str | None = None,
    prize: str | None = None,
) -> None:
    """Move a challenge section to a new venue and/or restate its prize."""
    if not _exists(
        conn, "SELECT 1 FROM FITNESS_SECTIONS WHERE CS_REF_ID = ?", (section_ref_id,)
    ):
        raise NotFound(f"no challenge section with reference {section_ref_id}")
    if location is None and prize is None:
        raise RepositoryError("nothing to update")

    with conn.transaction():
        if location is not None:
            changed = conn.execute(
                "UPDATE FITNESS_SECTIONS_DETAILS SET Location = ? WHERE CS_REF_ID = ?",
                (location, section_ref_id),
            )
            if changed == 0:
                raise NotFound(
                    f"challenge section {section_ref_id} has no schedule row to move"
                )
        if prize is not None:
            changed = conn.execute(
                "UPDATE FITNESS_CHALLENGE_WINNERS SET Prize = ? WHERE CS_REF_ID = ?",
                (prize, section_ref_id),
            )
            if changed == 0:
                raise NotFound(
                    f"challenge section {section_ref_id} has no winner to award"
                )


# ----------------------------------------------------------------------- read


def students_in_sport(conn: Connection, sport_id: int) -> list[Row]:
    get_sport(conn, sport_id)
    return conn.query(
        "SELECT spd.Student_ID, spd.First_Name, spd.Last_Name, ssd.Attendance "
        "FROM STUDENT_PERSONAL_DETAILS AS spd "
        "JOIN STUDENT_SPORT_DETAILS AS ssd ON ssd.Student_ID = spd.Student_ID "
        "WHERE ssd.Assigned_Sport = ? "
        "ORDER BY spd.Student_ID",
        (sport_id,),
    )


def staff_in_sport(conn: Connection, sport_id: int) -> list[Row]:
    get_sport(conn, sport_id)
    return conn.query(
        "SELECT sd.Staff_ID, sd.First_Name, sd.Last_Name, sp.Position "
        "FROM STAFF_DETAILS AS sd "
        "JOIN STAFF_POSITION AS sp ON sp.Staff_ID = sd.Staff_ID "
        "WHERE sp.Sport_ID = ? "
        "ORDER BY sd.Staff_ID",
        (sport_id,),
    )


def sports_on_day(conn: Connection, day: str) -> list[Row]:
    """Sports with at least one slot on the given day code, with head counts."""
    return conn.query(
        "SELECT s.Sport_ID, s.Sport_Name, sl.Time, COUNT(*) AS Booked "
        "FROM SPORTS AS s "
        "JOIN SPORTS_SLOT AS sl ON sl.Sport_ID = s.Sport_ID "
        "WHERE sl.Day = ? "
        "GROUP BY s.Sport_ID, s.Sport_Name, sl.Time "
        "ORDER BY sl.Time, s.Sport_Name",
        (day,),
    )


def equipment_on_date(conn: Connection, on_date: str) -> list[Row]:
    return conn.query(
        "SELECT em.Equipment_ID, e.Equipment_Name, em.Status, em.Staff_ID "
        "FROM EQUIPMENT_MAINTENANCE AS em "
        "JOIN EQUIPMENT AS e ON e.Equipment_ID = em.Equipment_ID "
        "WHERE em.Date = ? "
        "ORDER BY em.Equipment_ID",
        (on_date,),
    )


def search_sport_by_name(conn: Connection, name: str) -> list[Row]:
    """Exact-name lookup, joined to the venue and trainer."""
    return conn.query(
        "SELECT s.Sport_ID, s.Sport_Name, s.Capacity, s.No_of_Participants, "
        "s.Rules_Link, sl.Location, sl.Trainer "
        "FROM SPORTS AS s "
        "LEFT JOIN SPORTS_LOCATION AS sl ON sl.Sport_ID = s.Sport_ID "
        "WHERE s.Sport_Name = ? "
        "ORDER BY s.Sport_ID",
        (name,),
    )


LIKE_ESCAPE = "!"


def like_contains(fragment: str) -> str:
    """Build a LIKE pattern that treats the user's text literally.

    Binding the value stops injection but not wildcards: a bare `%` typed into a
    search box would otherwise match every row.  `%`, `_` and the escape
    character itself are escaped, and the query pairs this with ESCAPE '!',
    which both SQLite and MySQL understand.
    """
    escaped = (
        fragment.replace(LIKE_ESCAPE, LIKE_ESCAPE * 2)
        .replace("%", f"{LIKE_ESCAPE}%")
        .replace("_", f"{LIKE_ESCAPE}_")
    )
    return f"%{escaped}%"


def search_challenges(conn: Connection, fragment: str) -> list[Row]:
    """Substring search over challenge names."""
    return conn.query(
        "SELECT fc.Challenge_ID, fc.Challenge_Name, fcd.From_Date, fcd.To_Date, "
        "fcd.Registration_Deadline "
        "FROM FITNESS_CHALLENGES AS fc "
        "LEFT JOIN FITNESS_CHALLENGES_DETAILS AS fcd "
        "  ON fcd.Challenge_ID = fc.Challenge_ID "
        f"WHERE fc.Challenge_Name LIKE ? ESCAPE '{LIKE_ESCAPE}' "
        "ORDER BY fc.Challenge_ID",
        (like_contains(fragment),),
    )


# ------------------------------------------------------------------ aggregate


def funds_released_in_month(conn: Connection, month: int) -> dict[str, object]:
    """Total value of transactions whose fund was released in the given month."""
    if not 1 <= month <= 12:
        raise RepositoryError("month must be between 1 and 12")
    expr = month_expr(conn.dialect, "f.Date")
    row = conn.query_one(
        "SELECT COALESCE(SUM(t.Amount), 0) AS Total, COUNT(*) AS Releases "
        "FROM FUNDS AS f "
        "JOIN TRANSACTIONS AS t ON t.Transaction_ID = f.Transaction_ID "
        f"WHERE {expr} = ?",
        (month,),
    )
    return {"month": month, "total": row["Total"], "releases": row["Releases"]}


def total_pending_salary(conn: Connection) -> int:
    return int(
        conn.scalar("SELECT COALESCE(SUM(Pending_Salary), 0) FROM STAFF_PROFESSIONAL")
        or 0
    )


def average_students_per_sport(conn: Connection) -> float:
    """Mean enrolment across all sports, counting sports with nobody in them."""
    row = conn.query_one(
        "SELECT AVG(CountStudents) AS AverageEnrollment FROM ("
        "  SELECT s.Sport_ID, COUNT(ssd.Student_ID) AS CountStudents"
        "  FROM SPORTS AS s"
        "  LEFT JOIN STUDENT_SPORT_DETAILS AS ssd ON ssd.Assigned_Sport = s.Sport_ID"
        "  GROUP BY s.Sport_ID"
        ") AS PerSport"
    )
    value = row["AverageEnrollment"] if row else None
    return round(float(value), 2) if value is not None else 0.0


# ---------------------------------------------------------------- dashboards


def summary_counts(conn: Connection) -> dict[str, int]:
    """The headline numbers on the home screen."""
    return {
        "students": int(conn.scalar("SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS")),
        "staff": int(conn.scalar("SELECT COUNT(*) FROM STAFF_DETAILS")),
        "sports": int(conn.scalar("SELECT COUNT(*) FROM SPORTS")),
        "challenges": int(conn.scalar("SELECT COUNT(*) FROM FITNESS_CHALLENGES")),
        "equipment": int(conn.scalar("SELECT COALESCE(SUM(Quantity), 0) FROM EQUIPMENT")),
        "pending_salary": total_pending_salary(conn),
    }


def sport_enrolment(conn: Connection) -> list[Row]:
    """Per-sport enrolment against capacity, used for the dashboard chart."""
    return conn.query(
        "SELECT s.Sport_ID, s.Sport_Name, s.Capacity, "
        "COUNT(ssd.Student_ID) AS Enrolled "
        "FROM SPORTS AS s "
        "LEFT JOIN STUDENT_SPORT_DETAILS AS ssd ON ssd.Assigned_Sport = s.Sport_ID "
        "GROUP BY s.Sport_ID, s.Sport_Name, s.Capacity "
        "ORDER BY Enrolled DESC, s.Sport_Name"
    )


def funds_by_month(conn: Connection) -> list[Row]:
    expr = month_expr(conn.dialect, "f.Date")
    return conn.query(
        f"SELECT {expr} AS Month, COALESCE(SUM(t.Amount), 0) AS Total "
        "FROM FUNDS AS f "
        "JOIN TRANSACTIONS AS t ON t.Transaction_ID = f.Transaction_ID "
        f"GROUP BY {expr} "
        "ORDER BY Month"
    )


def equipment_status(conn: Connection) -> list[Row]:
    """Latest recorded maintenance status for each piece of equipment."""
    return conn.query(
        "SELECT e.Equipment_ID, e.Equipment_Name, e.Quantity, "
        "s.Sport_Name, em.Status, em.Date "
        "FROM EQUIPMENT AS e "
        "LEFT JOIN SPORTS AS s ON s.Sport_ID = e.Sport_ID "
        "LEFT JOIN EQUIPMENT_MAINTENANCE AS em "
        "  ON em.Equipment_ID = e.Equipment_ID "
        "  AND em.Date = (SELECT MAX(m2.Date) FROM EQUIPMENT_MAINTENANCE AS m2 "
        "                 WHERE m2.Equipment_ID = e.Equipment_ID) "
        "ORDER BY e.Equipment_ID"
    )


def attendance_by_department(conn: Connection) -> list[Row]:
    return conn.query(
        "SELECT sad.Department, COUNT(*) AS Students, "
        "ROUND(AVG(ssd.Attendance), 1) AS AvgAttendance "
        "FROM STUDENT_ACAD_DETAILS AS sad "
        "JOIN STUDENT_SPORT_DETAILS AS ssd ON ssd.Student_ID = sad.Student_ID "
        "GROUP BY sad.Department "
        "ORDER BY AvgAttendance DESC"
    )


def unassigned_students(conn: Connection) -> list[Row]:
    """Students not enrolled in any sport, which is the credit risk list."""
    return conn.query(
        "SELECT spd.Student_ID, spd.First_Name, spd.Last_Name, sad.Department "
        "FROM STUDENT_PERSONAL_DETAILS AS spd "
        "LEFT JOIN STUDENT_SPORT_DETAILS AS ssd ON ssd.Student_ID = spd.Student_ID "
        "LEFT JOIN STUDENT_ACAD_DETAILS AS sad ON sad.Student_ID = spd.Student_ID "
        "WHERE ssd.Assigned_Sport IS NULL "
        "ORDER BY spd.Student_ID"
    )


def list_sports(conn: Connection) -> list[Row]:
    return conn.query(
        "SELECT s.Sport_ID, s.Sport_Name, s.Capacity, s.No_of_Participants, "
        "sl.Location "
        "FROM SPORTS AS s "
        "LEFT JOIN SPORTS_LOCATION AS sl ON sl.Sport_ID = s.Sport_ID "
        "ORDER BY s.Sport_ID"
    )


def list_students(conn: Connection) -> list[Row]:
    return conn.query(
        "SELECT spd.Student_ID, spd.First_Name, spd.Last_Name, spd.Contact, "
        "sad.Department, sad.Course_Year, ssd.Attendance, s.Sport_Name "
        "FROM STUDENT_PERSONAL_DETAILS AS spd "
        "LEFT JOIN STUDENT_ACAD_DETAILS AS sad ON sad.Student_ID = spd.Student_ID "
        "LEFT JOIN STUDENT_SPORT_DETAILS AS ssd ON ssd.Student_ID = spd.Student_ID "
        "LEFT JOIN SPORTS AS s ON s.Sport_ID = ssd.Assigned_Sport "
        "ORDER BY spd.Student_ID"
    )


def list_staff(conn: Connection) -> list[Row]:
    return conn.query(
        "SELECT sd.Staff_ID, sd.First_Name, sd.Last_Name, sd.Contact, "
        "sp.Position, s.Sport_Name, spr.Type, spr.Total_Salary, spr.Pending_Salary "
        "FROM STAFF_DETAILS AS sd "
        "LEFT JOIN STAFF_POSITION AS sp ON sp.Staff_ID = sd.Staff_ID "
        "LEFT JOIN SPORTS AS s ON s.Sport_ID = sp.Sport_ID "
        "LEFT JOIN STAFF_PROFESSIONAL AS spr ON spr.Staff_ID = sd.Staff_ID "
        "ORDER BY sd.Staff_ID"
    )


def list_challenges(conn: Connection) -> list[Row]:
    return conn.query(
        "SELECT fc.Challenge_ID, fc.Challenge_Name, fcd.From_Date, fcd.To_Date, "
        "COUNT(DISTINCT fs.CS_REF_ID) AS Sections "
        "FROM FITNESS_CHALLENGES AS fc "
        "LEFT JOIN FITNESS_CHALLENGES_DETAILS AS fcd "
        "  ON fcd.Challenge_ID = fc.Challenge_ID "
        "LEFT JOIN FITNESS_SECTIONS AS fs ON fs.Challenge_ID = fc.Challenge_ID "
        "GROUP BY fc.Challenge_ID, fc.Challenge_Name, fcd.From_Date, fcd.To_Date "
        "ORDER BY fc.Challenge_ID"
    )


__all__ = [
    "CapacityExceeded",
    "DuplicateRecord",
    "NotFound",
    "RepositoryError",
    "add_fitness_challenge",
    "add_staff",
    "add_student",
    "attendance_by_department",
    "average_students_per_sport",
    "equipment_on_date",
    "equipment_status",
    "funds_by_month",
    "get_sport",
    "funds_released_in_month",
    "list_challenges",
    "list_sports",
    "list_staff",
    "list_students",
    "remove_equipment",
    "remove_sport",
    "search_challenges",
    "search_sport_by_name",
    "sport_enrolment",
    "sports_on_day",
    "staff_in_sport",
    "students_in_sport",
    "summary_counts",
    "total_pending_salary",
    "unassigned_students",
    "update_fitness_challenge",
    "update_staff",
    "update_student",
]
