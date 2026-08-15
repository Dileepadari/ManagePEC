<p align="center">
  <img src="assets/logo-mark.png" alt="ADK DEV" width="96">
</p>

# ManagePEC

A management application for a university Physical Education Centre - students,
staff, sports, fitness challenges, equipment and the money behind them, with a
web app and a terminal front end over the same database.

It grew out of the Data and Applications course project (Physical Education
Centre, team Samachara_Kendhram) and is now a working application: the schema
was corrected, the SQL was rewritten to be parameterised, the Flask skeleton was
finished, and the whole thing is covered by tests. See
[docs/CHANGES-FROM-PHASE4.md](docs/CHANGES-FROM-PHASE4.md) for the full list.

Developer setup, architecture and data model live in [DEVDOC.md](DEVDOC.md).

---

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m managepec.cli init-db     # creates data/pec.db with sample data
python run.py                       # http://127.0.0.1:5000
```

No database server is needed. SQLite is the default; MySQL is a config change
away if you want the original setup.

---

## Who uses it

- **PEC head** - the dashboard, the analysis page and the salary and fund figures
- **Coaches and trainers** - their sport's roster, attendance and slot timetable
- **Administration** - fund releases per month, pending salary, equipment spend
- **Maintenance staff** - the equipment inventory and its service history
- **Anyone comfortable with SQL** - the query console, without a shell account

---

## What you can do

### Dashboard

The headline counts (students, staff, sports, challenges, equipment units,
pending salary), enrolment per sport as a bar chart, funds released by month,
and the list of students who are not enrolled in anything, which is the list
that costs people their PE credit.

### Students

Every student with their department, course year, assigned sport, attendance and
contact number. Adding a student writes the personal, academic and sport records
together - either all three land or none do. A student can be added without a
sport, and a sport that is already at capacity is refused.

Contact numbers and attendance can be edited inline from the table.

### Staff

Coaches, trainers, physiotherapists and support staff, with their post, the
sport they are attached to, their type and their salary position. Adding a staff
member records their contract and post, and optionally a first scheduled task.
Pending salary above total salary is refused, as is making someone their own
supervisor.

### Sports

Every sport with its capacity, participant count and venue, a bar chart of
enrolment, and a day filter that shows which sports have slots on MWF, TTS, SUN
or ALL along with how many places are booked at each time.

Retiring a sport removes it and its slot bookings, and keeps every student,
staff post and piece of equipment that referenced it - the reference is simply
cleared. Nobody loses their record because a sport was discontinued.

### Challenges

Fitness challenges with their run dates, registration deadline and the sections
underneath them. Search matches any part of a challenge name. Adding one records
the challenge, its dates, a section, that section's date and venue, and
optionally a mentor and a winner with their prize. Dates that do not make sense
(an end before a start, a deadline after the start) are refused.

### Equipment

The inventory with quantities, the sport each item belongs to, and the most
recent maintenance record shown as a status: Good, Under Maintenance, Needs
Repair or Unrecorded. A date filter shows what was serviced on a given day.

Retiring an item removes it and its maintenance history, and keeps the funding
record it was bought with.

### Saved queries

Ten questions the centre asks often - full roster, spare capacity, attendance by
department, pending salary by role, funds per month, equipment needing
attention, challenge winners, the reporting line, open medical cases, and
students without a sport. Each one shows the SQL it runs next to the result, so
it doubles as a worked example.

### Query console

Run your own SELECT against the database. One statement at a time, starting with
SELECT or WITH; writes, DDL and anything that touches the server are refused
before they reach the driver, and results are capped. It is a reading tool, not
an admin console.

### Analysis

The aggregate and analysis questions in one page: average students per sport,
total pending salary, students without a sport, equipment units, funds released
in a chosen month, funds by month, and average attendance per department.

---

## The terminal front end

The same operations without a browser:

```bash
python -m managepec.cli              # interactive menu: 18 operations plus exit
python -m managepec.cli list staff   # students | staff | sports | challenges | equipment
python -m managepec.cli report       # the overview report
python -m managepec.cli init-db      # rebuild the database
```

The menu validates each answer as you type it, so a mistyped date is caught on
the line you typed it rather than eight prompts later, and it tells you what
actually happened rather than printing the SQL it was about to run.

---

## Project documents

The original course documents are kept in [docs/](docs):

- [Phase 1 - requirements and mini-world](docs/phase1-requirements.md)
- [Phase 2 - ER diagram and revisions](docs/phase2-er-diagram.md)
- [What changed from phase 4](docs/CHANGES-FROM-PHASE4.md)
