#!/usr/bin/env python3
"""CLI utility to synchronize all Markdown files in procedures/ into PostgreSQL."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import DATABASE_URL, PROCEDURES_DIR
from app.database import create_repository
from app.sync import sync_directory


def main() -> None:
    repo = create_repository(DATABASE_URL)
    print(f"[SYNC] Database engine: {repo.engine_name}")
    print(f"[SYNC] Procedures dir : {PROCEDURES_DIR}")
    repo.init_schema()
    stats = sync_directory(repo, PROCEDURES_DIR)
    print("[SYNC] Result:", json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"[SYNC] Total procedures in DB: {repo.count()}")


if __name__ == "__main__":
    main()
