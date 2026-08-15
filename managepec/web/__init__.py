"""Flask application factory.

    flask --app managepec.web run --debug
    python run.py

One connection is opened per request and closed on teardown, which is the piece
the phase-4 `app.py` was missing: it opened a SQLite connection at import time,
took a cursor from it, closed the connection and then never used either again.
"""

from __future__ import annotations

from flask import Flask, g

from ..config import Settings, load_settings
from ..db import Connection, Database


def get_db() -> Connection:
    """The connection for the current request, opened on first use."""
    if "db_conn" not in g:
        g.db_conn = current_database().connect()
    return g.db_conn


def current_database() -> Database:
    from flask import current_app

    return current_app.extensions["managepec_database"]


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or load_settings()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["MANAGEPEC_SETTINGS"] = settings
    app.config["MAX_QUERY_ROWS"] = settings.max_query_rows
    app.extensions["managepec_database"] = Database(settings)

    @app.teardown_appcontext
    def close_db(_exception: BaseException | None) -> None:
        conn = g.pop("db_conn", None)
        if conn is not None:
            conn.close()

    from .routes import bp

    app.register_blueprint(bp)
    return app


__all__ = ["create_app", "current_database", "get_db"]
