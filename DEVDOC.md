# ManagePEC - developer documentation

What the app does and who it is for is in [README.md](README.md). This file is
for changing the code.

---

## Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.10+ | uses `X \| None` annotations and `dict[str, ...]` |
| Web | Flask 3, server-rendered Jinja | no build step, no client framework, no JS at all |
| Database | SQLite (default) or MySQL 8 / MariaDB 10.4+ | SQLite so it runs and tests with no server; MySQL because that is what the project was written against |
| MySQL driver | PyMySQL | pure Python, no build toolchain |
| Tests | pytest | 175 on SQLite, 11 opt-in against a live MySQL |
| Styling | one hand-written stylesheet | replaced a vendored Bootstrap + jQuery + FontAwesome + LineIcons bundle |

There is no ORM. The SQL is written out, which is the point of the project.

---

## Layout

```
managepec/
  config.py        Settings, read once from the environment
  db.py            Database, Connection, dialect translation, script splitting
  models.py        input dataclasses and every field validator
  repository.py    every read and write, one function per operation
  presets.py       the saved queries shown on the Pre-Query page
  safe_sql.py      the read-only guard for the ad-hoc console
  cli.py           terminal front end
  web/
    __init__.py    create_app, per-request connection
    routes.py      one blueprint, nine pages plus a JSON endpoint
    templates/     base.html + one per page, _macros.html for tables and bars
    static/        app.css and the ADK DEV mark
schema/
  schema.sqlite.sql   DDL, SQLite dialect
  schema.mysql.sql    DDL, MySQL/MariaDB dialect - kept in step by hand
  seed.sql            sample data, loads into both
tests/              conftest + one file per module
docs/               course documents, the ER diagram, the phase-4 originals
run.py              development entrypoint
```

The dependency direction is one-way: `web` and `cli` both depend on
`repository`, which depends on `db` and `models`. Nothing goes back up. If you
find yourself importing `flask` below `web/`, something is in the wrong layer.

---

## The two-backend arrangement

`db.py` normalises the two drivers so nothing above it branches on the backend.

- **Placeholders.** All SQL is written with `?`. For MySQL,
  `translate_placeholders` rewrites `?` to `%s` and doubles every `%` (PyMySQL
  `%`-formats the whole statement, literals included). It skips `?` inside
  single-quoted strings.
- **Rows.** Both backends return `list[dict]` keyed by column name.
- **Dialect functions.** `month_expr(dialect, col)` and `year_expr` give the
  right spelling; the SQLite one is `strftime`, the MySQL one is `MONTH()`.
- **Scripts.** `executescript` runs a multi-statement file. SQLite has a native
  call; for MySQL `split_statements` splits on semicolons that are not inside a
  string or a comment.

If you add a query that needs a function the two dialects spell differently, add
a helper next to `month_expr` rather than branching at the call site.

### Adding a column

Both schema files, then the seed if it is `NOT NULL` without a default, then the
repository function, then the template. The SQLite and MySQL files use identical
table and column names on purpose - a test asserts every table exists, so a
rename that misses one file fails immediately.

---

## Data model

25 tables. The shape follows the phase-2 ER diagram
([docs/phase2-er-diagram.md](docs/phase2-er-diagram.md)); the corrections made
on top of the phase-4 dump are listed in
[docs/CHANGES-FROM-PHASE4.md](docs/CHANGES-FROM-PHASE4.md).

Two root entities:

- `STUDENT_PERSONAL_DETAILS` splits into `STUDENT_ACAD_DETAILS`,
  `STUDENT_SPORT_DETAILS` and `STUDENT_HEALTH_DETAILS`, all keyed on `Student_ID`.
- `STAFF_DETAILS` splits into `STAFF_PROFESSIONAL`, `STAFF_POSITION` and
  `STAFF_TASKS`.

`SPORTS` is referenced from `SPORTS_LOCATION`, `SPORTS_SLOT`,
`STUDENT_SPORT_DETAILS`, `STAFF_POSITION` and `EQUIPMENT`. Challenges run
`FITNESS_CHALLENGES` → `FITNESS_SECTIONS` → mentors and winners. Money runs
`TRANSACTIONS` → `FUNDS` → `EQUIPMENT_REGISTRATION`, with `EQUIPMENT_FUNDS`
tying a transaction to what it bought.

### The delete rules are the load-bearing part

The choice between `CASCADE` and `SET NULL` is what makes `remove_sport` and
`remove_equipment` single statements, so do not change one without reading the
matching repository function and test.

| Reference | Rule | Effect |
|---|---|---|
| `SPORTS_LOCATION.Sport_ID` | CASCADE | the venue row belongs to the sport |
| `SPORTS_SLOT.Sport_ID` | CASCADE | a booking for a retired sport is meaningless |
| `STUDENT_SPORT_DETAILS.Assigned_Sport` | SET NULL | the student stays, unenrolled |
| `STAFF_POSITION.Sport_ID` | SET NULL | the post stays, unattached |
| `STAFF_POSITION.Supervisor` | SET NULL | the report stays, unsupervised |
| `EQUIPMENT.Sport_ID` | SET NULL | the kit stays, unassigned |
| `EQUIPMENT_MAINTENANCE.Equipment_ID` | CASCADE | history belongs to the item |
| `EQUIPMENT_FUNDS.Equipment_ID` | SET NULL | the spend record outlives the item |
| all `*_DETAILS.<parent key>` | CASCADE | a detail row is part of its parent |

SQLite only enforces foreign keys with `PRAGMA foreign_keys = ON`, which
`Database._connect_sqlite` sets on every connection. Without it the SET NULL
rules silently do nothing, and the "retiring a sport keeps its students" tests
are what catch that.

### Constraints

`CHECK`s cover capacity (`No_of_Participants <= Capacity`), attendance (0-100),
non-negative credits, salary and quantity, and challenge date ordering
(`To_Date >= From_Date`, `Registration_Deadline <= From_Date`). They are the
backstop; `models.py` is what produces a readable message.

---

## Validation

Every value that reaches `repository` has been through a dataclass in
`models.py` - `StudentInput`, `StaffInput`, `ChallengeInput` - built by
`from_raw(dict)`. A failure raises `ValidationError`, which carries the field
name so the UI can point at it.

The field parsers (`parse_int`, `parse_date`, `parse_time`, `parse_contact`,
`parse_text`, `split_name`, `parse_day_code`) are used in two places: by
`from_raw`, and by the CLI's `ask_field`, which re-prompts on the line the user
typed. The double check is deliberate - the record is validated as a whole
regardless of which front end filled it in.

Add a field by adding it to the dataclass and its `from_raw`, then to the CLI
handler and the web form. The repository should never see a raw string.

---

## SQL safety

Two separate mechanisms, do not confuse them.

1. **Application queries.** SQL text is a constant in `repository.py`; values are
   bound. There is no f-string interpolation of user input anywhere. Dialect
   fragments (`month_expr`) are the only thing ever interpolated, and they come
   from a fixed table.
2. **The ad-hoc console.** `safe_sql.validate` blanks out literals and comments,
   then requires a single statement opening with SELECT or WITH and containing
   none of `FORBIDDEN_KEYWORDS`. `safe_sql.run` also caps rows at
   `MAX_QUERY_ROWS`.

`LIKE` searches go through `repository.like_contains`, which escapes `%`, `_`
and the escape character and pairs with `ESCAPE '!'`. Binding a parameter stops
injection but not wildcards: without this, a user typing `%` into the search box
matches every row.

---

## Web layer

`create_app(settings)` is the factory. One connection per request, stored on `g`,
closed in `teardown_appcontext`. Routes read the form, hand it to a dataclass,
hand that to the repository, and render - they contain no SQL.

`USER_ERRORS = (ValidationError, RepositoryError)` is the pair every handler
catches and flashes. Anything else is a bug and should surface as a 500.

Templates extend `base.html` and use two macros from `_macros.html`:
`data_table(columns, rows, empty)` and `bar_chart(rows, name, value, max)`.
There is no JavaScript on any page.

### Styling

`static/css/app.css` is tokens plus flexbox and grid. Light values are on bare
`:root`; dark values are repeated under both `@media (prefers-color-scheme: dark)`
(guarded with `:not([data-theme="light"])`) and `:root[data-theme="dark"]`.

Two things that have already bitten:

- `.bar-track` and `.bar-fill` are spans inside a grid row and need an explicit
  `display: block`, or `width`/`height` are ignored and the bars disappear.
- The brand is the ADK DEV **mark** in a tinted badge next to the app name, never
  the full wordmark - that asset is 476x524 and sizing it by width made it 165px
  tall, which ate the top of the phone layout. `.logo-mono` recolours it with
  `brightness(0)` / `brightness(0) invert(1)` so one file reads in both themes.
- `main` has no `max-width`. Cards and tables want the whole column; only running
  prose is held to a measure (`78ch`), and `form.stack` is capped at 1180px so a
  wide window does not stretch a twelve-field form into one row.
- Table headings go through the `column_label` filter, which turns `Student_ID`
  into `Student ID`. The query console and saved-query pages pass
  `raw_headers=true` to `data_table`, because there the column name is the answer.

Charts follow the project data-viz rules: one blue hue for a single-series
magnitude chart, bars scaled to the largest value in the series rather than to
capacity (scaling 3 against 100 makes every bar invisible), values direct-labelled
so no legend is needed, and the reserved four-colour status palette always paired
with a text label so colour never carries the meaning alone.

---

## Configuration

All optional; the defaults run.

| Variable | Default | Meaning |
|---|---|---|
| `MANAGEPEC_DB` | `sqlite` | `sqlite` or `mysql` |
| `MANAGEPEC_SQLITE_PATH` | `data/pec.db` | SQLite file |
| `MANAGEPEC_MYSQL_HOST` | `localhost` | |
| `MANAGEPEC_MYSQL_PORT` | `3306` | |
| `MANAGEPEC_MYSQL_USER` | `root` | |
| `MANAGEPEC_MYSQL_PASSWORD` | empty | |
| `MANAGEPEC_MYSQL_DB` | `PEC` | |
| `MANAGEPEC_SECRET_KEY` | `dev-only-change-me` | Flask session key - **set this in production** |
| `MANAGEPEC_MAX_QUERY_ROWS` | `500` | console row cap |
| `MANAGEPEC_HOST` / `MANAGEPEC_PORT` / `MANAGEPEC_DEBUG` | `127.0.0.1` / `5000` / `1` | `run.py` only |

---

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m managepec.cli init-db
python run.py
```

`init-db` drops and recreates every table, then loads `schema/seed.sql`. Use
`--no-seed` for empty tables.

### Against MySQL

```bash
mysql -u root -p -e "CREATE DATABASE PEC CHARACTER SET utf8mb4;"
export MANAGEPEC_DB=mysql MANAGEPEC_MYSQL_USER=root MANAGEPEC_MYSQL_PASSWORD=...
python -m managepec.cli init-db
```

---

## Tests

```bash
pytest                       # 175 tests, SQLite, no setup
pytest tests/test_web.py -v
```

Each test gets a fresh SQLite file built from the real `schema.sqlite.sql` and
`seed.sql`, so a broken DDL fails the suite rather than passing against a
hand-written fixture. Several tests assert against exact seed values (12
students, 7 sports, 130000 pending salary) - changing `seed.sql` means updating
those.

### The MySQL suite

Skipped unless pointed at a scratch database, because it drops every table in it:

```bash
mysql -u root -p -e "CREATE DATABASE managepec_test CHARACTER SET utf8mb4;"
MANAGEPEC_TEST_MYSQL_DB=managepec_test \
MANAGEPEC_TEST_MYSQL_USER=root \
MANAGEPEC_TEST_MYSQL_PASSWORD=... \
pytest tests/test_mysql_backend.py
```

It exists to prove the dialect translation and the delete rules behave the same
on both engines. Run it after touching `db.py` or either schema file.

---

## Deployment

`run.py` is development only. Behind a real server:

```bash
pip install gunicorn
MANAGEPEC_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') \
gunicorn 'managepec.web:create_app()'
```

The app has no authentication. Anyone who can reach it can add records and run
queries, so put it behind whatever the deployment already uses for access
control, and do not expose the query console to the open internet.

---

## Gotchas

- SQLite returns dates as strings and MySQL as `datetime.date`. Compare with
  `str(row["Date"])` in tests, and let the templates print whatever they get.
- `Connection.transaction()` commits on clean exit and rolls back on any
  exception. Repository writes use it; do not call `commit()` inside one.
- `repository` functions raise, they never print. Keep it that way or the web
  layer inherits terminal output.
- The CLI menu catches broad exceptions per option on purpose, so one bad answer
  does not end the session. That is a UI decision, not a pattern to copy.
- `data/` is gitignored. `init-db` recreates it.
- Error handlers use `@bp.app_errorhandler`, not `@bp.errorhandler`. A URL that
  matches no route belongs to no blueprint, so a blueprint-scoped 404 handler
  never fires and Flask serves its own unstyled page.
- `run.py` does not auto-reload with `MANAGEPEC_DEBUG=0`, and Jinja caches
  templates, so template edits need a restart when debug is off.
