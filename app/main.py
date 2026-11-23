"""FastAPI web application for Vietnamese Public Administrative Procedures."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import AUTO_SYNC_ON_STARTUP, BASE_DIR, DATABASE_URL, PROCEDURES_DIR
from app.database import BaseProcedureRepository, create_repository
from app.sync import save_and_ingest_markdown, sync_directory

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def create_app(
    database_url: str | None = None,
    procedures_dir: Path | None = None,
) -> FastAPI:
    proc_dir = (procedures_dir or PROCEDURES_DIR).resolve()
    repo: BaseProcedureRepository = create_repository(database_url or DATABASE_URL)
    state = {"initialized": False}

    def ensure_initialized() -> None:
        if not state["initialized"]:
            repo.init_schema()
            if AUTO_SYNC_ON_STARTUP:
                sync_directory(repo, proc_dir)
            state["initialized"] = True

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        ensure_initialized()
        yield

    app = FastAPI(
        title="Cổng Tra cứu Quy trình Thủ tục Hành chính Công Việt Nam",
        description="Tra cứu nhanh thủ tục hành chính, sơ đồ Mermaid trực quan và cập nhật mở từ file Markdown.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.state.repo = repo
    app.state.procedures_dir = proc_dir

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home(
        request: Request,
        q: str = Query(default="", max_length=150),
        ministry: str = Query(default="", max_length=120),
        sector: str = Query(default="", max_length=120),
    ):
        ensure_initialized()
        items = repo.search(q=q, ministry=ministry, sector=sector)
        facets = repo.list_facets()
        total_all = repo.count()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "items": items,
                "facets": facets,
                "q": q,
                "selected_ministry": ministry,
                "selected_sector": sector,
                "total_all": total_all,
                "engine_name": repo.engine_name,
            },
        )

    @app.get("/thu-tuc/{slug}", response_class=HTMLResponse)
    def procedure_detail(request: Request, slug: str):
        ensure_initialized()
        item = repo.get_by_slug(slug)
        if not item:
            raise HTTPException(status_code=404, detail="Không tìm thấy quy trình thủ tục này.")
        return templates.TemplateResponse(
            request=request,
            name="detail.html",
            context={
                "item": item,
                "engine_name": repo.engine_name,
            },
        )

    @app.get("/cap-nhat", response_class=HTMLResponse)
    def upload_page(request: Request, msg: str = "", error: str = ""):
        ensure_initialized()
        template_file = proc_dir / "_template.md"
        template_text = template_file.read_text(encoding="utf-8") if template_file.exists() else ""
        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={
                "template_text": template_text,
                "total_all": repo.count(),
                "engine_name": repo.engine_name,
                "msg": msg,
                "error": error,
            },
        )

    @app.post("/cap-nhat/upload")
    async def upload_markdown_file(
        file: UploadFile = File(...),
        subfolder: str = Form(default="custom"),
    ):
        ensure_initialized()
        if not file.filename or not file.filename.lower().endswith(".md"):
            return RedirectResponse(
                url="/cap-nhat?error=Vui+lòng+chọn+tệp+định+dạng+.md+(Markdown).",
                status_code=303,
            )
        raw_bytes = await file.read()
        try:
            text = raw_bytes.decode("utf-8")
            result = save_and_ingest_markdown(
                repo=repo,
                procedures_dir=proc_dir,
                raw_content=text,
                subfolder=subfolder,
                filename=file.filename,
            )
        except Exception as exc:
            return RedirectResponse(url=f"/cap-nhat?error=Lỗi+đọc+file:+{exc}", status_code=303)

        return RedirectResponse(url=f"/thu-tuc/{result['slug']}", status_code=303)

    @app.post("/cap-nhat/soan-moi")
    def create_markdown_from_editor(
        markdown_content: str = Form(...),
        subfolder: str = Form(default="custom"),
    ):
        ensure_initialized()
        if not markdown_content.strip():
            return RedirectResponse(
                url="/cap-nhat?error=Nội+dung+Markdown+không+được+để+trống.",
                status_code=303,
            )
        try:
            result = save_and_ingest_markdown(
                repo=repo,
                procedures_dir=proc_dir,
                raw_content=markdown_content,
                subfolder=subfolder,
            )
        except Exception as exc:
            return RedirectResponse(url=f"/cap-nhat?error=Lỗi+lưu+thủ+tục:+{exc}", status_code=303)
        return RedirectResponse(url=f"/thu-tuc/{result['slug']}", status_code=303)

    @app.post("/cap-nhat/sync")
    def trigger_sync_from_ui():
        ensure_initialized()
        stats = sync_directory(repo, proc_dir)
        msg = (
            f"Đã quét {stats['scanned']} file: "
            f"thêm mới {stats['inserted']}, cập nhật {stats['updated']}, giữ nguyên {stats['unchanged']}."
        )
        return RedirectResponse(url=f"/cap-nhat?msg={msg}", status_code=303)

    # --- REST API endpoints ---
    @app.get("/api/procedures")
    def api_search(
        q: str = Query(default="", max_length=150),
        ministry: str = Query(default="", max_length=120),
        sector: str = Query(default="", max_length=120),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> dict[str, Any]:
        ensure_initialized()
        items = repo.search(q=q, ministry=ministry, sector=sector, limit=limit)
        return {
            "count": len(items),
            "engine": repo.engine_name,
            "items": items,
        }

    @app.get("/api/procedures/{slug}")
    def api_detail(slug: str) -> dict[str, Any]:
        ensure_initialized()
        item = repo.get_by_slug(slug)
        if not item:
            raise HTTPException(status_code=404, detail="Procedure not found")
        return item

    @app.post("/api/sync")
    def api_sync() -> dict[str, Any]:
        ensure_initialized()
        return sync_directory(repo, proc_dir)

    @app.post("/api/upload")
    async def api_upload(
        file: UploadFile = File(...),
        subfolder: str = Form(default="custom"),
    ) -> JSONResponse:
        ensure_initialized()
        if not file.filename or not file.filename.lower().endswith(".md"):
            raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp .md (Markdown).")
        raw = (await file.read()).decode("utf-8")
        result = save_and_ingest_markdown(repo, proc_dir, raw, subfolder=subfolder, filename=file.filename)
        return JSONResponse(result, status_code=201)

    @app.get("/api/template", response_class=PlainTextResponse)
    def api_download_template():
        template_file = proc_dir / "_template.md"
        if not template_file.exists():
            raise HTTPException(status_code=404, detail="Template not found")
        return PlainTextResponse(
            template_file.read_text(encoding="utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="mau-thu-tuc-hanh-chinh.md"'},
        )

    return app


app = create_app()
