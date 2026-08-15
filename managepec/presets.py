"""The saved queries shown on the Pre-Query page.

Each entry carries the SQL it runs, so the page can show the statement next to
its result rather than describing it.  They are plain SELECTs and are executed
through the same read-only guard as the query console.
"""

from __future__ import annotations

from dataclasses import dataclass

from .db import month_expr


@dataclass(frozen=True)
class Preset:
    key: str
    title: str
    description: str
    sql: str


def presets(dialect: str) -> list[Preset]:
    """Build the preset list for a dialect (only the month function differs)."""
    month = month_expr(dialect, "f.Date")
    return [
        Preset(
            key="roster",
            title="Roster for every sport",
            description="Who is enrolled where, with the venue and the trainer.",
            sql=(
                "SELECT s.Sport_Name, sl.Location,\n"
                "       spd.Student_ID, spd.First_Name, spd.Last_Name,\n"
                "       ssd.Attendance\n"
                "FROM SPORTS AS s\n"
                "LEFT JOIN SPORTS_LOCATION AS sl ON sl.Sport_ID = s.Sport_ID\n"
                "LEFT JOIN STUDENT_SPORT_DETAILS AS ssd\n"
                "       ON ssd.Assigned_Sport = s.Sport_ID\n"
                "LEFT JOIN STUDENT_PERSONAL_DETAILS AS spd\n"
                "       ON spd.Student_ID = ssd.Student_ID\n"
                "ORDER BY s.Sport_Name, spd.Student_ID"
            ),
        ),
        Preset(
            key="capacity",
            title="Spare capacity per sport",
            description="Free places left, so trials can be opened where it matters.",
            sql=(
                "SELECT s.Sport_Name, s.Capacity,\n"
                "       COUNT(ssd.Student_ID) AS Enrolled,\n"
                "       s.Capacity - COUNT(ssd.Student_ID) AS Spare\n"
                "FROM SPORTS AS s\n"
                "LEFT JOIN STUDENT_SPORT_DETAILS AS ssd\n"
                "       ON ssd.Assigned_Sport = s.Sport_ID\n"
                "GROUP BY s.Sport_ID, s.Sport_Name, s.Capacity\n"
                "ORDER BY Spare DESC"
            ),
        ),
        Preset(
            key="attendance",
            title="Attendance by department",
            description="Average attendance per department, worst last.",
            sql=(
                "SELECT sad.Department,\n"
                "       COUNT(*) AS Students,\n"
                "       ROUND(AVG(ssd.Attendance), 1) AS AvgAttendance\n"
                "FROM STUDENT_ACAD_DETAILS AS sad\n"
                "JOIN STUDENT_SPORT_DETAILS AS ssd\n"
                "  ON ssd.Student_ID = sad.Student_ID\n"
                "GROUP BY sad.Department\n"
                "ORDER BY AvgAttendance DESC"
            ),
        ),
        Preset(
            key="pending_salary",
            title="Pending salary by staff type",
            description="What the centre still owes, grouped by role.",
            sql=(
                "SELECT sp.Type,\n"
                "       COUNT(*) AS Staff,\n"
                "       SUM(sp.Pending_Salary) AS Pending\n"
                "FROM STAFF_PROFESSIONAL AS sp\n"
                "GROUP BY sp.Type\n"
                "ORDER BY Pending DESC"
            ),
        ),
        Preset(
            key="funds",
            title="Funds released per month",
            description="Transaction value grouped by the month the fund cleared.",
            sql=(
                f"SELECT {month} AS Month,\n"
                "       COUNT(*) AS Releases,\n"
                "       SUM(t.Amount) AS Total\n"
                "FROM FUNDS AS f\n"
                "JOIN TRANSACTIONS AS t\n"
                "  ON t.Transaction_ID = f.Transaction_ID\n"
                f"GROUP BY {month}\n"
                "ORDER BY Month"
            ),
        ),
        Preset(
            key="maintenance",
            title="Equipment needing attention",
            description="Latest maintenance record per item, excluding 'Good'.",
            sql=(
                "SELECT e.Equipment_ID, e.Equipment_Name, e.Quantity,\n"
                "       em.Date, em.Status\n"
                "FROM EQUIPMENT AS e\n"
                "JOIN EQUIPMENT_MAINTENANCE AS em\n"
                "  ON em.Equipment_ID = e.Equipment_ID\n"
                " AND em.Date = (SELECT MAX(m.Date)\n"
                "                FROM EQUIPMENT_MAINTENANCE AS m\n"
                "                WHERE m.Equipment_ID = e.Equipment_ID)\n"
                "WHERE em.Status <> 'Good'\n"
                "ORDER BY em.Date DESC"
            ),
        ),
        Preset(
            key="winners",
            title="Challenge winners",
            description="Every prize awarded, with the challenge and the section.",
            sql=(
                "SELECT fc.Challenge_Name, fs.Section_Name,\n"
                "       spd.First_Name, spd.Last_Name, fcw.Prize\n"
                "FROM FITNESS_CHALLENGE_WINNERS AS fcw\n"
                "JOIN FITNESS_SECTIONS AS fs ON fs.CS_REF_ID = fcw.CS_REF_ID\n"
                "JOIN FITNESS_CHALLENGES AS fc\n"
                "  ON fc.Challenge_ID = fs.Challenge_ID\n"
                "JOIN STUDENT_PERSONAL_DETAILS AS spd\n"
                "  ON spd.Student_ID = fcw.Winner_ID\n"
                "ORDER BY fc.Challenge_ID, fs.CS_REF_ID"
            ),
        ),
        Preset(
            key="supervision",
            title="Who reports to whom",
            description="Staff joined to their supervisor through the self reference.",
            sql=(
                "SELECT sd.Staff_ID, sd.First_Name AS Staff,\n"
                "       sp.Position, boss.First_Name AS Supervisor\n"
                "FROM STAFF_DETAILS AS sd\n"
                "JOIN STAFF_POSITION AS sp ON sp.Staff_ID = sd.Staff_ID\n"
                "LEFT JOIN STAFF_DETAILS AS boss\n"
                "       ON boss.Staff_ID = sp.Supervisor\n"
                "ORDER BY sd.Staff_ID"
            ),
        ),
        Preset(
            key="medical",
            title="Open medical cases",
            description="Injuries and conditions with their treatment and recovery date.",
            sql=(
                "SELECT spd.Student_ID, spd.First_Name, spd.Last_Name,\n"
                "       mh.Type, mhd.Severity, mhd.Treatment, mhd.Recovery\n"
                "FROM MEDICAL_HISTORY AS mh\n"
                "JOIN MEDICAL_HISTORY_DETAILS AS mhd ON mhd.Med_ID = mh.Med_ID\n"
                "JOIN STUDENT_PERSONAL_DETAILS AS spd\n"
                "  ON spd.Student_ID = mh.Student_ID\n"
                "ORDER BY mhd.Recovery DESC"
            ),
        ),
        Preset(
            key="unassigned",
            title="Students without a sport",
            description="The credit-risk list: enrolled in nothing.",
            sql=(
                "SELECT spd.Student_ID, spd.First_Name, spd.Last_Name,\n"
                "       sad.Department, sad.Course_Year\n"
                "FROM STUDENT_PERSONAL_DETAILS AS spd\n"
                "LEFT JOIN STUDENT_SPORT_DETAILS AS ssd\n"
                "       ON ssd.Student_ID = spd.Student_ID\n"
                "LEFT JOIN STUDENT_ACAD_DETAILS AS sad\n"
                "       ON sad.Student_ID = spd.Student_ID\n"
                "WHERE ssd.Assigned_Sport IS NULL\n"
                "ORDER BY spd.Student_ID"
            ),
        ),
    ]


def find(dialect: str, key: str) -> Preset | None:
    for preset in presets(dialect):
        if preset.key == key:
            return preset
    return None


__all__ = ["Preset", "find", "presets"]
