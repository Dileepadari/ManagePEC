"""HTTP routes.

Every handler is thin: read the form, hand it to `models` for validation, hand
that to `repository`, then render.  No SQL is written here and no user value is
ever concatenated into a statement.
"""

from __future__ import annotations

import re

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from .. import presets as preset_module
from .. import repository as repo
from .. import safe_sql
from ..models import (
    ChallengeInput,
    StaffInput,
    StudentInput,
    ValidationError,
    parse_contact,
    parse_int,
)
from . import get_db

bp = Blueprint("pec", __name__)

USER_ERRORS = (ValidationError, repo.RepositoryError)


@bp.app_template_filter("blank")
def blank(value: object) -> str:
    """Render NULLs as a dash rather than the word None."""
    return "-" if value is None else str(value)


@bp.app_template_filter("column_label")
def column_label(column: str) -> str:
    """Turn a database column name into a heading a person would write.

    `Student_ID` becomes "Student ID" and `AvgAttendance` becomes "Avg
    Attendance". The stylesheet upper-cases table headings, so this is about
    losing the underscores and splitting the runs-together names, not about case.
    """
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(column).replace("_", " "))
    return " ".join(spaced.split()) or str(column)


@bp.app_context_processor
def inject_nav() -> dict[str, object]:
    return {"nav_items": NAV_ITEMS}


NAV_ITEMS = [
    ("pec.dashboard", "Dashboard"),
    ("pec.students", "Students"),
    ("pec.staff", "Staff"),
    ("pec.sports", "Sports"),
    ("pec.challenges", "Challenges"),
    ("pec.equipment", "Equipment"),
    ("pec.saved_queries", "Saved queries"),
    ("pec.query_console", "Query console"),
    ("pec.analysis", "Analysis"),
]


# ------------------------------------------------------------------ dashboard


@bp.route("/")
def dashboard():
    conn = get_db()
    enrolment = repo.sport_enrolment(conn)
    funds = repo.funds_by_month(conn)
    return render_template(
        "dashboard.html",
        counts=repo.summary_counts(conn),
        enrolment=enrolment,
        max_enrolled=max((row["Enrolled"] for row in enrolment), default=0) or 1,
        max_capacity=max((row["Capacity"] for row in enrolment), default=1),
        funds=funds,
        max_fund=max((row["Total"] for row in funds), default=1),
        unassigned=repo.unassigned_students(conn),
        average=repo.average_students_per_sport(conn),
    )


# ------------------------------------------------------------------- students


@bp.route("/students", methods=["GET", "POST"])
def students():
    conn = get_db()
    if request.method == "POST":
        try:
            repo.add_student(conn, StudentInput.from_raw(request.form.to_dict()))
            flash("Student added.", "success")
            return redirect(url_for("pec.students"))
        except USER_ERRORS as exc:
            flash(str(exc), "error")
    return render_template(
        "students.html",
        students=repo.list_students(conn),
        sports=repo.list_sports(conn),
        form=request.form,
    )


@bp.route("/students/<int:student_id>/update", methods=["POST"])
def update_student(student_id: int):
    conn = get_db()
    contact = request.form.get("contact") or None
    attendance = request.form.get("attendance") or None
    try:
        repo.update_student(
            conn,
            student_id,
            contact=None if contact is None else parse_contact("contact", contact),
            attendance=None
            if attendance is None
            else parse_int("attendance", attendance, minimum=0, maximum=100),
        )
        flash(f"Student {student_id} updated.", "success")
    except USER_ERRORS as exc:
        flash(str(exc), "error")
    return redirect(url_for("pec.students"))


# ---------------------------------------------------------------------- staff


@bp.route("/staff", methods=["GET", "POST"])
def staff():
    conn = get_db()
    if request.method == "POST":
        try:
            repo.add_staff(conn, StaffInput.from_raw(request.form.to_dict()))
            flash("Staff member added.", "success")
            return redirect(url_for("pec.staff"))
        except USER_ERRORS as exc:
            flash(str(exc), "error")
    return render_template(
        "staff.html",
        staff=repo.list_staff(conn),
        sports=repo.list_sports(conn),
        pending_total=repo.total_pending_salary(conn),
        form=request.form,
    )


# --------------------------------------------------------------------- sports


@bp.route("/sports")
def sports():
    conn = get_db()
    day = request.args.get("day", "").strip().upper()
    on_day = repo.sports_on_day(conn, day) if day else None
    return render_template(
        "sports.html",
        sports=repo.list_sports(conn),
        enrolment=repo.sport_enrolment(conn),
        day=day,
        on_day=on_day,
    )


@bp.route("/sports/<int:sport_id>/retire", methods=["POST"])
def retire_sport(sport_id: int):
    conn = get_db()
    try:
        sport = repo.remove_sport(conn, sport_id)
        flash(
            f"Retired {sport['Sport_Name']}. Students, staff and equipment kept "
            "their records with the sport reference cleared.",
            "success",
        )
    except USER_ERRORS as exc:
        flash(str(exc), "error")
    return redirect(url_for("pec.sports"))


# ----------------------------------------------------------------- challenges


@bp.route("/challenges", methods=["GET", "POST"])
def challenges():
    conn = get_db()
    if request.method == "POST":
        try:
            repo.add_fitness_challenge(
                conn, ChallengeInput.from_raw(request.form.to_dict())
            )
            flash("Challenge added.", "success")
            return redirect(url_for("pec.challenges"))
        except USER_ERRORS as exc:
            flash(str(exc), "error")

    search = request.args.get("q", "").strip()
    listing = (
        repo.search_challenges(conn, search) if search else repo.list_challenges(conn)
    )
    return render_template(
        "challenges.html", challenges=listing, search=search, form=request.form
    )


# ------------------------------------------------------------------ equipment


@bp.route("/equipment")
def equipment():
    conn = get_db()
    on_date = request.args.get("date", "").strip()
    serviced = repo.equipment_on_date(conn, on_date) if on_date else None
    return render_template(
        "equipment.html",
        equipment=repo.equipment_status(conn),
        on_date=on_date,
        serviced=serviced,
    )


@bp.route("/equipment/<int:equipment_id>/retire", methods=["POST"])
def retire_equipment(equipment_id: int):
    conn = get_db()
    try:
        removed = repo.remove_equipment(conn, equipment_id)
        flash(f"Removed {removed['Equipment_Name']}.", "success")
    except USER_ERRORS as exc:
        flash(str(exc), "error")
    return redirect(url_for("pec.equipment"))


# -------------------------------------------------------------- saved queries


@bp.route("/saved-queries")
def saved_queries():
    conn = get_db()
    available = preset_module.presets(conn.dialect)
    key = request.args.get("key", available[0].key)
    chosen = preset_module.find(conn.dialect, key) or available[0]

    columns, rows, truncated = safe_sql.run(
        conn, chosen.sql, current_app.config["MAX_QUERY_ROWS"]
    )
    return render_template(
        "saved_queries.html",
        presets=available,
        chosen=chosen,
        columns=columns,
        rows=rows,
        truncated=truncated,
    )


# ------------------------------------------------------------- query console


@bp.route("/query", methods=["GET", "POST"])
def query_console():
    conn = get_db()
    sql = request.form.get("sql", "") if request.method == "POST" else ""
    columns: list[str] = []
    rows: list[dict] = []
    truncated = False
    error = None
    would_change = False

    if request.method == "POST":
        limit = current_app.config["MAX_QUERY_ROWS"]
        try:
            columns, rows, truncated = safe_sql.run(conn, sql, limit)
        except safe_sql.UnsafeQuery as exc:
            error = str(exc)
            would_change = exc.changes_database
        except Exception as exc:
            conn.rollback()
            error = f"The database rejected that query: {exc}"

    return render_template(
        "query.html",
        sql=sql,
        columns=columns,
        rows=rows,
        truncated=truncated,
        error=error,
        would_change=would_change,
        ran=request.method == "POST" and error is None,
        limit=current_app.config["MAX_QUERY_ROWS"],
    )


# ------------------------------------------------------------------- analysis


@bp.route("/analysis")
def analysis():
    conn = get_db()
    month = request.args.get("month", type=int)
    monthly = None
    if month is not None:
        try:
            monthly = repo.funds_released_in_month(conn, month)
        except repo.RepositoryError as exc:
            flash(str(exc), "error")
    return render_template(
        "analysis.html",
        counts=repo.summary_counts(conn),
        average=repo.average_students_per_sport(conn),
        pending=repo.total_pending_salary(conn),
        attendance=repo.attendance_by_department(conn),
        funds=repo.funds_by_month(conn),
        enrolment=repo.sport_enrolment(conn),
        unassigned=repo.unassigned_students(conn),
        month=month,
        monthly=monthly,
    )


# ------------------------------------------------------------------------ api


@bp.route("/api/summary")
def api_summary():
    conn = get_db()
    return jsonify(
        {
            "counts": repo.summary_counts(conn),
            "average_students_per_sport": repo.average_students_per_sport(conn),
            "enrolment": repo.sport_enrolment(conn),
            "funds_by_month": repo.funds_by_month(conn),
        }
    )


# app_errorhandler, not errorhandler: a URL that matches no route belongs to no
# blueprint, so a blueprint-scoped handler never sees it and Flask serves its own
# unstyled page instead.
@bp.app_errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="Page not found."), 404


@bp.app_errorhandler(500)
def server_error(_error):
    return (
        render_template(
            "error.html",
            code=500,
            message="Something went wrong at our end. The error has been logged.",
        ),
        500,
    )
