"""Open Markdown directory synchronization & live ingestion into the database."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.database import BaseProcedureRepository
from app.parser import parse_markdown_content, parse_markdown_file, slugify


def sync_directory(
    repo: BaseProcedureRepository,
    procedures_dir: Path,
) -> dict[str, Any]:
    """Scan all .md files under procedures_dir (excluding files starting with '_') and upsert."""
    stats = {
        "scanned": 0,
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "errors": [],
    }
    if not procedures_dir.exists():
        return stats

    for md_file in sorted(procedures_dir.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue
        stats["scanned"] += 1
        try:
            record = parse_markdown_file(md_file, base_dir=procedures_dir)
            result = repo.upsert(record)
            stats[result] += 1
        except Exception as exc:
            stats["errors"].append({"file": str(md_file.name), "error": str(exc)})

    return stats


def save_and_ingest_markdown(
    repo: BaseProcedureRepository,
    procedures_dir: Path,
    raw_content: str,
    subfolder: str = "custom",
    filename: str | None = None,
) -> dict[str, Any]:
    """Save a new/updated Markdown file into procedures/<subfolder>/ and index into DB immediately."""
    record = parse_markdown_content(raw_content)
    safe_folder = slugify(subfolder) or "custom"
    target_dir = procedures_dir / safe_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{slugify(Path(filename).stem)}.md" if filename else f"{record.slug}.md"
    target_path = target_dir / safe_name
    target_path.write_text(raw_content.strip() + "\n", encoding="utf-8")

    # Re-parse with relative source_path so DB stores exact location
    final_record = parse_markdown_file(target_path, base_dir=procedures_dir)
    status = repo.upsert(final_record)
    return {
        "status": status,
        "slug": final_record.slug,
        "title": final_record.title,
        "source_path": final_record.source_path,
    }
