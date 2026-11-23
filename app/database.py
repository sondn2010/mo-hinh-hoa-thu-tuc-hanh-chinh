"""Database repository supporting PostgreSQL (primary, FTS + unaccent + pg_trgm) and SQLite fallback."""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.config import DATABASE_URL, SCHEMA_PATH
from app.parser import ProcedureRecord, strip_vietnamese_accents


class BaseProcedureRepository(ABC):
    engine_name: str = "base"

    @abstractmethod
    def init_schema(self) -> None:
        ...

    @abstractmethod
    def upsert(self, record: ProcedureRecord) -> str:
        """Insert or update a procedure. Returns 'inserted', 'updated', or 'unchanged'."""
        ...

    @abstractmethod
    def search(
        self,
        q: str = "",
        ministry: str = "",
        sector: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    def list_facets(self) -> dict[str, list[dict[str, Any]]]:
        ...

    @abstractmethod
    def count(self) -> int:
        ...


class PostgresProcedureRepository(BaseProcedureRepository):
    """Primary production backend using PostgreSQL unaccent + tsvector GIN + pg_trgm."""

    engine_name = "PostgreSQL (unaccent + tsvector + pg_trgm)"

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def _connect(self):
        try:
            import psycopg
            from psycopg.rows import dict_row

            return psycopg.connect(self.dsn, row_factory=dict_row)
        except ImportError:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)

    def init_schema(self) -> None:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    def upsert(self, record: ProcedureRecord) -> str:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT content_hash FROM procedures WHERE slug = %s",
                    (record.slug,),
                )
                existing = cur.fetchone()
                if existing and existing["content_hash"] == record.content_hash:
                    return "unchanged"

                cur.execute(
                    """
                    INSERT INTO procedures (
                        slug, code, title, ministry, sector, level, online_level,
                        processing_time, fee, official_url, portal_url, portal_name,
                        tags, summary, mermaid_code, steps_json, body_markdown,
                        body_html, source_path, content_hash, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s::jsonb, %s,
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        code = EXCLUDED.code,
                        title = EXCLUDED.title,
                        ministry = EXCLUDED.ministry,
                        sector = EXCLUDED.sector,
                        level = EXCLUDED.level,
                        online_level = EXCLUDED.online_level,
                        processing_time = EXCLUDED.processing_time,
                        fee = EXCLUDED.fee,
                        official_url = EXCLUDED.official_url,
                        portal_url = EXCLUDED.portal_url,
                        portal_name = EXCLUDED.portal_name,
                        tags = EXCLUDED.tags,
                        summary = EXCLUDED.summary,
                        mermaid_code = EXCLUDED.mermaid_code,
                        steps_json = EXCLUDED.steps_json,
                        body_markdown = EXCLUDED.body_markdown,
                        body_html = EXCLUDED.body_html,
                        source_path = EXCLUDED.source_path,
                        content_hash = EXCLUDED.content_hash,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        record.slug,
                        record.code,
                        record.title,
                        record.ministry,
                        record.sector,
                        record.level,
                        record.online_level,
                        record.processing_time,
                        record.fee,
                        record.official_url,
                        record.portal_url,
                        record.portal_name,
                        record.tags,
                        record.summary,
                        record.mermaid_code,
                        json.dumps(record.steps, ensure_ascii=False),
                        record.body_markdown,
                        record.body_html,
                        record.source_path,
                        record.content_hash,
                        record.updated_at,
                    ),
                )
            conn.commit()
            return "updated" if existing else "inserted"

    def search(
        self,
        q: str = "",
        ministry: str = "",
        sector: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        q_clean = q.strip()
        conditions = []
        params: list[Any] = []

        if ministry.strip():
            conditions.append("ministry = %s")
            params.append(ministry.strip())
        if sector.strip():
            conditions.append("sector = %s")
            params.append(sector.strip())

        where_filter = f"AND {' AND '.join(conditions)}" if conditions else ""

        with self._connect() as conn:
            with conn.cursor() as cur:
                if q_clean:
                    sql = f"""
                        WITH q AS (
                            SELECT
                                websearch_to_tsquery('simple', immutable_unaccent(%s)) AS tsq,
                                lower(immutable_unaccent(%s)) AS plain_q
                        )
                        SELECT
                            slug, code, title, ministry, sector, level, online_level,
                            processing_time, fee, official_url, portal_url, portal_name,
                            tags, summary, updated_at, steps_json,
                            (
                                COALESCE(ts_rank_cd(search_vector, q.tsq), 0) * 2.0
                                + similarity(search_plain, q.plain_q)
                            ) AS rank
                        FROM procedures, q
                        WHERE (
                            search_vector @@ q.tsq
                            OR search_plain ILIKE '%%' || q.plain_q || '%%'
                            OR similarity(search_plain, q.plain_q) > 0.18
                        )
                        {where_filter}
                        ORDER BY rank DESC, title ASC
                        LIMIT %s
                    """
                    cur.execute(sql, [q_clean, q_clean, *params, limit])
                else:
                    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
                    sql = f"""
                        SELECT
                            slug, code, title, ministry, sector, level, online_level,
                            processing_time, fee, official_url, portal_url, portal_name,
                            tags, summary, updated_at, steps_json
                        FROM procedures
                        {where_clause}
                        ORDER BY ministry ASC, title ASC
                        LIMIT %s
                    """
                    cur.execute(sql, [*params, limit])
                rows = [dict(r) for r in cur.fetchall()]
                for r in rows:
                    r["steps"] = r.pop("steps_json", []) or []
                return rows

    def get_by_slug(self, slug: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        slug, code, title, ministry, sector, level, online_level,
                        processing_time, fee, official_url, portal_url, portal_name,
                        tags, summary, mermaid_code, steps_json, body_markdown,
                        body_html, source_path, updated_at
                    FROM procedures
                    WHERE slug = %s
                    """,
                    (slug,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                data = dict(row)
                data["steps"] = data.pop("steps_json", []) or []
                return data

    def list_facets(self) -> dict[str, list[dict[str, Any]]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ministry AS name, COUNT(*)::int AS count FROM procedures GROUP BY ministry ORDER BY count DESC, ministry ASC"
                )
                ministries = [dict(r) for r in cur.fetchall()]
                cur.execute(
                    "SELECT sector AS name, COUNT(*)::int AS count FROM procedures GROUP BY sector ORDER BY count DESC, sector ASC"
                )
                sectors = [dict(r) for r in cur.fetchall()]
                return {"ministries": ministries, "sectors": sectors}

    def count(self) -> int:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*)::int AS total FROM procedures")
                row = cur.fetchone()
                return int(row["total"]) if row else 0


class SQLiteProcedureRepository(BaseProcedureRepository):
    """Lightweight local fallback (accent-insensitive search) for testing without Postgres."""

    engine_name = "SQLite FTS5 Local (dvc_local.db)"

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS procedures (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug            TEXT NOT NULL UNIQUE,
                    code            TEXT NOT NULL DEFAULT '',
                    title           TEXT NOT NULL,
                    ministry        TEXT NOT NULL DEFAULT '',
                    sector          TEXT NOT NULL DEFAULT '',
                    level           TEXT NOT NULL DEFAULT '',
                    online_level    TEXT NOT NULL DEFAULT '',
                    processing_time TEXT NOT NULL DEFAULT '',
                    fee             TEXT NOT NULL DEFAULT '',
                    official_url    TEXT NOT NULL DEFAULT '',
                    portal_url      TEXT NOT NULL DEFAULT '',
                    portal_name     TEXT NOT NULL DEFAULT '',
                    tags_json       TEXT NOT NULL DEFAULT '[]',
                    summary         TEXT NOT NULL DEFAULT '',
                    mermaid_code    TEXT NOT NULL DEFAULT '',
                    steps_json      TEXT NOT NULL DEFAULT '[]',
                    body_markdown   TEXT NOT NULL DEFAULT '',
                    body_html       TEXT NOT NULL DEFAULT '',
                    source_path     TEXT NOT NULL DEFAULT '',
                    content_hash    TEXT NOT NULL DEFAULT '',
                    updated_at      TEXT NOT NULL DEFAULT '',
                    search_plain    TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.commit()

    def upsert(self, record: ProcedureRecord) -> str:
        search_plain = strip_vietnamese_accents(
            " ".join(
                [
                    record.title,
                    record.code,
                    record.ministry,
                    record.sector,
                    " ".join(record.tags),
                    record.summary,
                    record.body_markdown,
                ]
            )
        ).lower()

        with self._connect() as conn:
            cur = conn.execute("SELECT content_hash FROM procedures WHERE slug = ?", (record.slug,))
            existing = cur.fetchone()
            if existing and existing["content_hash"] == record.content_hash:
                return "unchanged"

            conn.execute(
                """
                INSERT INTO procedures (
                    slug, code, title, ministry, sector, level, online_level,
                    processing_time, fee, official_url, portal_url, portal_name,
                    tags_json, summary, mermaid_code, steps_json, body_markdown,
                    body_html, source_path, content_hash, updated_at, search_plain
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    code = excluded.code,
                    title = excluded.title,
                    ministry = excluded.ministry,
                    sector = excluded.sector,
                    level = excluded.level,
                    online_level = excluded.online_level,
                    processing_time = excluded.processing_time,
                    fee = excluded.fee,
                    official_url = excluded.official_url,
                    portal_url = excluded.portal_url,
                    portal_name = excluded.portal_name,
                    tags_json = excluded.tags_json,
                    summary = excluded.summary,
                    mermaid_code = excluded.mermaid_code,
                    steps_json = excluded.steps_json,
                    body_markdown = excluded.body_markdown,
                    body_html = excluded.body_html,
                    source_path = excluded.source_path,
                    content_hash = excluded.content_hash,
                    updated_at = excluded.updated_at,
                    search_plain = excluded.search_plain
                """,
                (
                    record.slug,
                    record.code,
                    record.title,
                    record.ministry,
                    record.sector,
                    record.level,
                    record.online_level,
                    record.processing_time,
                    record.fee,
                    record.official_url,
                    record.portal_url,
                    record.portal_name,
                    json.dumps(record.tags, ensure_ascii=False),
                    record.summary,
                    record.mermaid_code,
                    json.dumps(record.steps, ensure_ascii=False),
                    record.body_markdown,
                    record.body_html,
                    record.source_path,
                    record.content_hash,
                    record.updated_at,
                    search_plain,
                ),
            )
            conn.commit()
            return "updated" if existing else "inserted"

    def _hydrate(self, row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["tags"] = json.loads(d.pop("tags_json", "[]") or "[]")
        d["steps"] = json.loads(d.pop("steps_json", "[]") or "[]")
        return d

    def search(
        self,
        q: str = "",
        ministry: str = "",
        sector: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: list[Any] = []
        if ministry.strip():
            conditions.append("ministry = ?")
            params.append(ministry.strip())
        if sector.strip():
            conditions.append("sector = ?")
            params.append(sector.strip())

        q_norm = strip_vietnamese_accents(q.strip()).lower()
        tokens = [t for t in q_norm.split() if t]
        for tok in tokens:
            conditions.append("search_plain LIKE ?")
            params.append(f"%{tok}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"""
            SELECT
                slug, code, title, ministry, sector, level, online_level,
                processing_time, fee, official_url, portal_url, portal_name,
                tags_json, summary, updated_at, steps_json
            FROM procedures
            {where_clause}
            ORDER BY ministry ASC, title ASC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = [self._hydrate(r) for r in conn.execute(sql, [*params, limit]).fetchall()]

        if tokens:
            def score(item: dict[str, Any]) -> int:
                title_plain = strip_vietnamese_accents(item["title"]).lower()
                code_plain = item["code"].lower()
                tags_plain = strip_vietnamese_accents(" ".join(item["tags"])).lower()
                s = 0
                for tok in tokens:
                    if tok in code_plain:
                        s += 10
                    if tok in title_plain:
                        s += 6
                    if tok in tags_plain:
                        s += 3
                return s

            rows.sort(key=lambda r: (-score(r), r["title"]))
        return rows

    def get_by_slug(self, slug: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    slug, code, title, ministry, sector, level, online_level,
                    processing_time, fee, official_url, portal_url, portal_name,
                    tags_json, summary, mermaid_code, steps_json, body_markdown,
                    body_html, source_path, updated_at
                FROM procedures
                WHERE slug = ?
                """,
                (slug,),
            ).fetchone()
            return self._hydrate(row) if row else None

    def list_facets(self) -> dict[str, list[dict[str, Any]]]:
        with self._connect() as conn:
            ministries = [
                dict(r)
                for r in conn.execute(
                    "SELECT ministry AS name, COUNT(*) AS count FROM procedures GROUP BY ministry ORDER BY count DESC, ministry ASC"
                ).fetchall()
            ]
            sectors = [
                dict(r)
                for r in conn.execute(
                    "SELECT sector AS name, COUNT(*) AS count FROM procedures GROUP BY sector ORDER BY count DESC, sector ASC"
                ).fetchall()
            ]
            return {"ministries": ministries, "sectors": sectors}

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM procedures").fetchone()
            return int(row["total"]) if row else 0


def create_repository(database_url: str | None = None) -> BaseProcedureRepository:
    url = (database_url or DATABASE_URL).strip()
    if url.startswith(("postgresql://", "postgres://")):
        return PostgresProcedureRepository(url)
    if url.startswith("sqlite:///"):
        return SQLiteProcedureRepository(url.removeprefix("sqlite:///"))
    return SQLiteProcedureRepository(url)
