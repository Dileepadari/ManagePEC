"""CLI tests: argument handling, table rendering and the interactive menu."""

from __future__ import annotations

import builtins

import pytest

from managepec import cli
from managepec.config import Settings


@pytest.fixture()
def cli_env(monkeypatch, settings: Settings, database):
    """Point `cli.main` at the test database."""
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    return settings


# ------------------------------------------------------------------ rendering


def test_format_table_renders_headers_and_a_count():
    output = cli.format_table([{"a": 1, "b": "x"}, {"a": 22, "b": "yy"}])
    lines = output.splitlines()
    assert lines[0].split() == ["a", "b"]
    assert lines[-1] == "2 row(s)"


def test_format_table_shows_nulls_as_a_dash():
    assert "-" in cli.format_table([{"a": None}])


def test_format_table_uses_the_empty_message():
    assert cli.format_table([], "nothing here") == "nothing here"


# --------------------------------------------------------------- subcommands


def test_init_db_creates_a_seeded_database(monkeypatch, tmp_path, capsys):
    settings = Settings(backend="sqlite", sqlite_path=tmp_path / "fresh.db")
    monkeypatch.setattr(cli, "load_settings", lambda: settings)

    assert cli.main(["init-db"]) == 0
    assert settings.sqlite_path.exists()
    assert "with sample data" in capsys.readouterr().out

    from managepec.db import Database

    conn = Database(settings).connect()
    try:
        assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 7
    finally:
        conn.close()


def test_init_db_without_seed_creates_empty_tables(monkeypatch, tmp_path):
    settings = Settings(backend="sqlite", sqlite_path=tmp_path / "empty.db")
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    assert cli.main(["init-db", "--no-seed"]) == 0

    from managepec.db import Database

    conn = Database(settings).connect()
    try:
        assert conn.scalar("SELECT COUNT(*) FROM SPORTS") == 0
    finally:
        conn.close()


@pytest.mark.parametrize(
    "what", ["students", "staff", "sports", "challenges", "equipment"]
)
def test_list_subcommand(cli_env, capsys, what):
    assert cli.main(["list", what]) == 0
    assert "row(s)" in capsys.readouterr().out


def test_report_subcommand(cli_env, capsys):
    assert cli.main(["report"]) == 0
    output = capsys.readouterr().out
    assert "Overview" in output
    assert "Enrolment per sport" in output


def test_unknown_subcommand_exits_with_an_error():
    with pytest.raises(SystemExit):
        cli.main(["nonsense"])


# ---------------------------------------------------------------------- menu


def feed(monkeypatch, answers):
    """Replace input() with a scripted sequence."""
    queue = list(answers)

    def fake_input(_prompt=""):
        if not queue:
            raise EOFError
        return queue.pop(0)

    monkeypatch.setattr(builtins, "input", fake_input)


def test_menu_exits_on_the_exit_option(monkeypatch, conn, capsys):
    feed(monkeypatch, [str(len(cli.MENU) + 1)])
    assert cli.run_menu(conn) == 0


def test_menu_rejects_a_non_numeric_choice(monkeypatch, conn, capsys):
    feed(monkeypatch, ["abc", str(len(cli.MENU) + 1)])
    cli.run_menu(conn)
    assert "Enter the number of an option." in capsys.readouterr().out


def test_menu_rejects_an_out_of_range_choice(monkeypatch, conn, capsys):
    feed(monkeypatch, ["99", str(len(cli.MENU) + 1)])
    cli.run_menu(conn)
    assert "Pick a number between" in capsys.readouterr().out


def test_menu_adds_a_student(monkeypatch, conn, capsys):
    feed(
        monkeypatch,
        [
            "1",  # add a student
            "80",
            "Priya Menon",
            "2005-02-02",
            "+91-9800099999",
            "CSE",
            "2024",
            "0",
            "1",
            "75",
            str(len(cli.MENU) + 1),
        ],
    )
    cli.run_menu(conn)
    assert "Added student 80" in capsys.readouterr().out
    assert conn.scalar(
        "SELECT COUNT(*) FROM STUDENT_PERSONAL_DETAILS WHERE Student_ID = 80"
    ) == 1


def test_menu_reprompts_on_a_bad_field_instead_of_failing_at_the_end(
    monkeypatch, conn, capsys
):
    """A bad answer is caught on the line it was typed, not nine prompts later."""
    feed(
        monkeypatch,
        [
            "1",
            "81",
            "OnlyOneName",  # rejected here
            "Asha Rao",  # accepted on the retry
            "01/01/2005",  # rejected here
            "2005-01-01",  # accepted on the retry
            "+91-9800011188",
            "CSE",
            "2024",
            "0",
            "",  # no sport
            "65",
            str(len(cli.MENU) + 1),
        ],
    )
    cli.run_menu(conn)
    output = capsys.readouterr().out
    assert "needs both a first and a last name" in output
    assert "must be a date in YYYY-MM-DD form" in output
    assert "Added student 81 (Asha Rao)." in output


def test_menu_reports_a_repository_error_and_carries_on(monkeypatch, conn, capsys):
    feed(
        monkeypatch,
        [
            "1",
            "1",  # student 1 already exists in the seed
            "Asha Rao",
            "2005-01-01",
            "+91-9800011199",
            "CSE",
            "2024",
            "0",
            "",
            "65",
            str(len(cli.MENU) + 1),
        ],
    )
    cli.run_menu(conn)
    assert "Error: student 1 already exists" in capsys.readouterr().out


def test_menu_retire_sport_can_be_cancelled(monkeypatch, conn, capsys):
    feed(monkeypatch, ["4", "1", "n", str(len(cli.MENU) + 1)])
    cli.run_menu(conn)
    assert "Cancelled." in capsys.readouterr().out
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS WHERE Sport_ID = 1") == 1


def test_menu_retire_sport_confirmed(monkeypatch, conn):
    feed(monkeypatch, ["4", "1", "y", str(len(cli.MENU) + 1)])
    cli.run_menu(conn)
    assert conn.scalar("SELECT COUNT(*) FROM SPORTS WHERE Sport_ID = 1") == 0


def test_menu_pending_salary(monkeypatch, conn, capsys):
    feed(monkeypatch, ["14", str(len(cli.MENU) + 1)])
    cli.run_menu(conn)
    assert "Total pending salary: 130000" in capsys.readouterr().out


def test_menu_search_challenges(monkeypatch, conn, capsys):
    feed(monkeypatch, ["16", "Yoga", str(len(cli.MENU) + 1)])
    cli.run_menu(conn)
    assert "Yoga Challenge" in capsys.readouterr().out


def test_menu_stops_cleanly_on_eof(monkeypatch, conn):
    feed(monkeypatch, [])
    assert cli.run_menu(conn) == 0
