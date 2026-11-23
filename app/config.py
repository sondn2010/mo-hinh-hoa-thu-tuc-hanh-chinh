"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"
PROCEDURES_DIR = Path(os.getenv("PROCEDURES_DIR", str(BASE_DIR / "procedures"))).resolve()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'dvc_local.db'}")
AUTO_SYNC_ON_STARTUP = os.getenv("AUTO_SYNC_ON_STARTUP", "true").lower() in ("1", "true", "yes")
