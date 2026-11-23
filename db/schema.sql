-- PostgreSQL 16+ Schema tối ưu tìm kiếm tiếng Việt (có dấu & không dấu)
-- Sử dụng extension unaccent + pg_trgm + Full-Text Search (tsvector + GIN)

CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Tạo immutable wrapper cho unaccent để dùng trong GENERATED column / index
CREATE OR REPLACE FUNCTION immutable_unaccent(text)
RETURNS text
LANGUAGE sql
IMMUTABLE PARALLEL SAFE STRICT AS
$func$
    SELECT public.unaccent('public.unaccent', $1)
$func$;

-- Bảng chính lưu trữ quy trình thủ tục hành chính (đồng bộ từ file Markdown)
CREATE TABLE IF NOT EXISTS procedures (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    code            TEXT NOT NULL DEFAULT '',
    title           TEXT NOT NULL,
    ministry        TEXT NOT NULL DEFAULT 'Chưa phân loại',
    sector          TEXT NOT NULL DEFAULT 'Chung',
    level           TEXT NOT NULL DEFAULT '',
    online_level    TEXT NOT NULL DEFAULT '',
    processing_time TEXT NOT NULL DEFAULT '',
    fee             TEXT NOT NULL DEFAULT '',
    official_url    TEXT NOT NULL DEFAULT '',
    portal_url      TEXT NOT NULL DEFAULT '',
    portal_name     TEXT NOT NULL DEFAULT '',
    tags            TEXT[] NOT NULL DEFAULT '{}',
    summary         TEXT NOT NULL DEFAULT '',
    mermaid_code    TEXT NOT NULL DEFAULT '',
    steps_json      JSONB NOT NULL DEFAULT '[]'::jsonb,
    body_markdown   TEXT NOT NULL DEFAULT '',
    body_html       TEXT NOT NULL DEFAULT '',
    source_path     TEXT NOT NULL DEFAULT '',
    content_hash    TEXT NOT NULL DEFAULT '',
    updated_at      TEXT NOT NULL DEFAULT '',
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Cột chuẩn hóa không dấu phục vụ tìm kiếm mờ (trigram)
    search_plain    TEXT NOT NULL DEFAULT '',

    -- Cột tsvector đánh trọng số A/B/C/D cho Full-Text Search tiếng Việt không dấu
    search_vector   TSVECTOR
);

-- Trigger tự động cập nhật search_plain & search_vector khi INSERT/UPDATE
CREATE OR REPLACE FUNCTION procedures_search_trigger() RETURNS trigger AS $$
DECLARE
    tags_text TEXT;
BEGIN
    tags_text := array_to_string(COALESCE(NEW.tags, '{}'), ' ');

    NEW.search_plain := lower(immutable_unaccent(
        COALESCE(NEW.title, '') || ' ' ||
        COALESCE(NEW.code, '') || ' ' ||
        COALESCE(NEW.ministry, '') || ' ' ||
        COALESCE(NEW.sector, '') || ' ' ||
        tags_text || ' ' ||
        COALESCE(NEW.summary, '')
    ));

    NEW.search_vector :=
        setweight(to_tsvector('simple', immutable_unaccent(COALESCE(NEW.title, ''))), 'A') ||
        setweight(to_tsvector('simple', immutable_unaccent(COALESCE(NEW.code, ''))), 'A') ||
        setweight(to_tsvector('simple', immutable_unaccent(tags_text)), 'B') ||
        setweight(to_tsvector('simple', immutable_unaccent(COALESCE(NEW.ministry, '') || ' ' || COALESCE(NEW.sector, ''))), 'B') ||
        setweight(to_tsvector('simple', immutable_unaccent(COALESCE(NEW.summary, ''))), 'C') ||
        setweight(to_tsvector('simple', immutable_unaccent(COALESCE(NEW.body_markdown, ''))), 'D');

    NEW.synced_at := NOW();
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_procedures_search ON procedures;
CREATE TRIGGER trg_procedures_search
    BEFORE INSERT OR UPDATE ON procedures
    FOR EACH ROW EXECUTE FUNCTION procedures_search_trigger();

-- Chỉ mục tối ưu tìm kiếm
CREATE INDEX IF NOT EXISTS idx_procedures_search_vector ON procedures USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_procedures_search_plain_trgm ON procedures USING GIN (search_plain gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_procedures_ministry ON procedures (ministry);
CREATE INDEX IF NOT EXISTS idx_procedures_sector ON procedures (sector);
CREATE INDEX IF NOT EXISTS idx_procedures_code ON procedures (code);
