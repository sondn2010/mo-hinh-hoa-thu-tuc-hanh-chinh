"""Markdown + YAML Frontmatter + Mermaid parser for Vietnamese public procedures."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import markdown
import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
STEP_LINE_RE = re.compile(r"^\s*\d+\.\s+\*\*(.+?)\*\*\s*(?:[—–:\-]\s*)?(.*)$")


def strip_vietnamese_accents(text: str) -> str:
    """Remove Vietnamese diacritics for accent-insensitive search & slugging."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def slugify(text: str) -> str:
    plain = strip_vietnamese_accents(text).lower()
    plain = re.sub(r"[^a-z0-9]+", "-", plain).strip("-")
    return plain or "thu-tuc"


@dataclass
class ProcedureRecord:
    slug: str
    code: str
    title: str
    ministry: str
    sector: str
    level: str
    online_level: str
    processing_time: str
    fee: str
    official_url: str
    portal_url: str
    portal_name: str
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    mermaid_code: str = ""
    steps: list[dict[str, str]] = field(default_factory=list)
    body_markdown: str = ""
    body_html: str = ""
    source_path: str = ""
    content_hash: str = ""
    updated_at: str = ""


def _extract_steps(body_md: str) -> list[dict[str, str]]:
    """Extract concise numbered steps from '## Các bước thực hiện...' section."""
    steps: list[dict[str, str]] = []
    in_steps_section = False
    for line in body_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading_lower = strip_vietnamese_accents(stripped).lower()
            in_steps_section = "cac buoc" in heading_lower or "trinh tu" in heading_lower
            continue
        if in_steps_section:
            m = STEP_LINE_RE.match(line)
            if m:
                step_title = m.group(1).strip()
                step_desc = m.group(2).strip()
                # Convert inline markdown links in step description to HTML
                step_desc_html = markdown.markdown(step_desc, extensions=["extra"]).removeprefix("<p>").removesuffix("</p>")
                steps.append({
                    "index": str(len(steps) + 1),
                    "title": step_title,
                    "description": step_desc,
                    "description_html": step_desc_html,
                })
    return steps


def _render_markdown_without_mermaid(body_md: str) -> str:
    """Render Markdown to HTML while removing the raw mermaid fence (rendered separately)."""
    cleaned = MERMAID_BLOCK_RE.sub("", body_md)
    # Remove the top H1 if duplicated by page header
    cleaned = re.sub(r"^\s*#\s+.+?\n+", "", cleaned, count=1)
    # Remove empty '## Sơ đồ quy trình' heading if nothing remains under it
    cleaned = re.sub(r"##\s+Sơ đồ quy trình\s*\n+(?=##|\Z)", "", cleaned)
    html = markdown.markdown(
        cleaned,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )
    # Open external links in a new tab safely
    html = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener noreferrer"',
        html,
    )
    return html


def parse_markdown_content(raw_text: str, source_path: str = "") -> ProcedureRecord:
    """Parse raw Markdown text with YAML frontmatter into a ProcedureRecord."""
    content_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    meta: dict[str, Any] = {}
    body_md = raw_text

    match = FRONTMATTER_RE.match(raw_text.lstrip("\ufeff"))
    if match:
        meta_raw, body_md = match.group(1), match.group(2)
        loaded = yaml.safe_load(meta_raw)
        if isinstance(loaded, dict):
            meta = loaded

    # Fallback title from first H1 if not in frontmatter
    title = str(meta.get("title") or "").strip()
    if not title:
        h1 = re.search(r"^\s*#\s+(.+)$", body_md, re.MULTILINE)
        title = h1.group(1).strip() if h1 else Path(source_path or "thu-tuc").stem

    slug = str(meta.get("slug") or "").strip() or slugify(title)

    mermaid_match = MERMAID_BLOCK_RE.search(body_md)
    mermaid_code = mermaid_match.group(1).strip() if mermaid_match else ""

    raw_tags = meta.get("tags") or []
    if isinstance(raw_tags, str):
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    elif isinstance(raw_tags, list):
        tags = [str(t).strip() for t in raw_tags if str(t).strip()]
    else:
        tags = []

    steps = _extract_steps(body_md)
    body_html = _render_markdown_without_mermaid(body_md)

    return ProcedureRecord(
        slug=slug,
        code=str(meta.get("code") or "").strip(),
        title=title,
        ministry=str(meta.get("ministry") or "Chưa phân loại").strip(),
        sector=str(meta.get("sector") or "Hành chính công").strip(),
        level=str(meta.get("level") or "").strip(),
        online_level=str(meta.get("online_level") or "").strip(),
        processing_time=str(meta.get("processing_time") or "").strip(),
        fee=str(meta.get("fee") or "").strip(),
        official_url=str(meta.get("official_url") or "").strip(),
        portal_url=str(meta.get("portal_url") or meta.get("official_url") or "").strip(),
        portal_name=str(meta.get("portal_name") or "Cổng Dịch vụ công Quốc gia").strip(),
        tags=tags,
        summary=str(meta.get("summary") or "").strip(),
        mermaid_code=mermaid_code,
        steps=steps,
        body_markdown=body_md.strip(),
        body_html=body_html,
        source_path=source_path,
        content_hash=content_hash,
        updated_at=str(meta.get("updated_at") or "").strip(),
    )


def parse_markdown_file(file_path: Path, base_dir: Path | None = None) -> ProcedureRecord:
    raw_text = file_path.read_text(encoding="utf-8")
    rel_path = str(file_path.relative_to(base_dir)) if base_dir else str(file_path)
    return parse_markdown_content(raw_text, source_path=rel_path)
