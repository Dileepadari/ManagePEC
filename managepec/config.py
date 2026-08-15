"""Runtime configuration, read once from the environment.

Everything has a working default so that `python -m managepec.cli` and
`flask --app managepec.web run` both start with no setup beyond creating the
SQLite file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = PROJECT_ROOT / "schema"
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "data" / "pec.db"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    """Resolved settings for one process."""

    backend: str = "sqlite"
    sqlite_path: Path = DEFAULT_SQLITE_PATH

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "PEC"

    secret_key: str = "dev-only-change-me"
    max_query_rows: int = 500

    def __post_init__(self) -> None:
        if self.backend not in {"sqlite", "mysql"}:
            raise ValueError(
                f"MANAGEPEC_DB must be 'sqlite' or 'mysql', got {self.backend!r}"
            )


def load_settings() -> Settings:
    """Build Settings from the current environment."""
    backend = os.environ.get("MANAGEPEC_DB", "sqlite").strip().lower()
    sqlite_path = Path(
        os.environ.get("MANAGEPEC_SQLITE_PATH", str(DEFAULT_SQLITE_PATH))
    ).expanduser()

    return Settings(
        backend=backend,
        sqlite_path=sqlite_path,
        mysql_host=os.environ.get("MANAGEPEC_MYSQL_HOST", "localhost"),
        mysql_port=_env_int("MANAGEPEC_MYSQL_PORT", 3306),
        mysql_user=os.environ.get("MANAGEPEC_MYSQL_USER", "root"),
        mysql_password=os.environ.get("MANAGEPEC_MYSQL_PASSWORD", ""),
        mysql_database=os.environ.get("MANAGEPEC_MYSQL_DB", "PEC"),
        secret_key=os.environ.get("MANAGEPEC_SECRET_KEY", "dev-only-change-me"),
        max_query_rows=_env_int("MANAGEPEC_MAX_QUERY_ROWS", 500),
    )


__all__ = [
    "PROJECT_ROOT",
    "SCHEMA_DIR",
    "DEFAULT_SQLITE_PATH",
    "Settings",
    "load_settings",
    "_env_bool",
]
