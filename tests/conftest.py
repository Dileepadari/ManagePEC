"""Shared fixtures.

Every test runs against a throwaway SQLite file built from the real schema and
seed files, so the tests exercise the same DDL that ships.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from managepec.config import Settings  # noqa: E402
from managepec.db import Connection, Database  # noqa: E402


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    return Settings(
        backend="sqlite",
        sqlite_path=tmp_path / "pec.db",
        secret_key="test-key",
        max_query_rows=50,
    )


@pytest.fixture()
def database(settings: Settings) -> Database:
    db = Database(settings)
    conn = db.connect()
    db.initialise(conn, with_seed=True)
    conn.close()
    return db


@pytest.fixture()
def conn(database: Database):
    connection: Connection = database.connect()
    yield connection
    connection.close()


@pytest.fixture()
def app(database: Database, settings: Settings):
    flask = pytest.importorskip("flask")  # noqa: F841
    from managepec.web import create_app

    application = create_app(settings)
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()
