# What changed from the phase-4 submission

The course submission lived in `Data-Applications/Project/phase4` (a MySQL dump
and a single `pec.py`) and `Data-Applications/website` (a Flask skeleton). Both
originals are kept in this folder as `legacy-phase4-dump.sql` and
`legacy-phase4-cli.py.txt` so the changes below can be checked against them.

## Correctness

| Was | Now |
|---|---|
| `addStudent` asked for the name, sport and attendance twice, so half the answers were discarded | each field is asked once |
| `removeEquipment` ran `UPDATE FROM EQUIPMENT_FUNDS ...`, which is not valid SQL and always threw | one `DELETE`, with the schema clearing the funding link |
| `removeSport` set `Assigned_Sport = NULL` after a `DELETE` that had already cascaded those rows away, so students, staff posts and equipment were deleted along with the sport | the foreign keys use `ON DELETE SET NULL` for the nullable references; the records survive with the reference cleared |
| `updateStudent`/`updateStaff` printed "updated" for IDs that did not exist | the row is checked first and a `NotFound` is raised |
| `updateStaff` referenced `staff_id` in its `except` block before it could be assigned | inputs are parsed before any statement runs |
| every insert was built with `%`-formatting, so a quote in a name broke the statement and a crafted one rewrote it | every value is a bound parameter |
| `STAFF_TASKS` had `Staff_ID` alone as its primary key, allowing one task per person | primary key is `(Staff_ID, Day, Time)` |
| `SPORTS_SLOT` had `Student_ID` alone as its primary key, allowing one slot per student | primary key is `(Student_ID, Sport_ID, Day, Time)` |
| `FITNESS_CHALLENGE_WINNERS` and `..._MENTORS` allowed one winner and one mentor per section | both are `(CS_REF_ID, <person>)` bridges |
| `EQUIPMENT_MAINTENANCE` allowed one check per item, ever | primary key is `(Equipment_ID, Date)` |
| `Attendence`, `Date_of_birth`, `Pending_salary` were spelled inconsistently between the dump and the script | `Attendance`, `Date_of_Birth`, `Pending_Salary` throughout |
| `EXTRACT(MONTH FROM ...)` tied the aggregates to MySQL | the month expression is chosen per dialect |
| `app.py` opened a SQLite connection at import, took a cursor, closed the connection, and never used either | one connection per request, closed on teardown |
| the Flask app had four routes, two of which rendered empty templates | nine pages, all backed by real queries |
| the query page had a form that posted to nothing | a read-only console with a guard and a row cap |

## Additions

- A validation layer (`managepec/models.py`), shared by the CLI and the web forms.
- A SQL guard (`managepec/safe_sql.py`) for the ad-hoc console: reads run, writes
  are shown and confirmed first, and statement-stacking or server/file access is
  refused outright.
- Pagination on every list screen, keeping the active filter.
- SQLite support so the project runs and tests with no server; MySQL still works.
- Capacity, attendance, salary and date-order `CHECK` constraints in the schema.
- Indexes on the columns the application filters and joins on.
- 175 tests on SQLite plus 11 opt-in tests against a live MySQL server.
- The vendored Bootstrap, jQuery, FontAwesome and LineIcons bundle was dropped in
  favour of one stylesheet, so the site loads nothing from the network.
