#!/usr/bin/env python3
"""
Công cụ tự động thu thập toàn bộ Thủ tục Hành chính Công từ CSDL Quốc gia (dichvucong.gov.vn),
tự động sinh file Markdown (.md) chuẩn hóa kèm sơ đồ Mermaid và nạp trực tiếp vào PostgreSQL.

Cách sử dụng trên máy có Internet:
  # 1. Thử nghiệm lấy 50 thủ tục đầu tiên và nạp vào DB:
  python scripts/crawl_dvc.py --limit 50 --sync

  # 2. Lấy theo từ khóa hoặc bộ/ngành (VD: "hộ chiếu", "đất đai", "thuế"):
  python scripts/crawl_dvc.py --keyword "đất đai" --limit 200 --sync

  # 3. Thu thập TOÀN BỘ thủ tục hành chính công trên Cổng DVC Quốc gia (~6.000+ thủ tục):
  python scripts/crawl_dvc.py --all --batch-size 50 --delay 0.4 --sync
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import DATABASE_URL, PROCEDURES_DIR
from app.database import create_repository
from app.parser import slugify
from app.sync import sync_directory

REST_ENDPOINTS = [
    "https://dichvucong.gov.vn/jsp/rest.jsp",
    "https://vpcp.dichvucong.gov.vn/jsp/rest.jsp",
]

DETAIL_URL_TPL = "https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-hanh-chinh.html?ma_thu_tuc={code}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://dichvucong.gov.vn/p/home/dvc-tthc-thu-tuc-hanh-chinh.html",
}


def clean_html_text(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", str(raw), flags=re.IGNORECASE)
    text = re.sub(r"</p>|</li>|</tr>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def post_dvc_rest(params_dict: dict[str, Any], timeout: int = 25) -> Any:
    """Call Cổng Dịch vụ công Quốc gia REST endpoint with automatic mirror fallback."""
    payload = urllib.parse.urlencode({"params": json.dumps(params_dict, ensure_ascii=False)}).encode("utf-8")
    last_err: Exception | None = None
    for endpoint in REST_ENDPOINTS:
        req = urllib.request.Request(endpoint, data=payload, headers=HEADERS, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace").strip()
                return json.loads(raw)
        except Exception as exc:
            last_err = exc
    raise RuntimeError(f"Không thể kết nối tới Cổng DVC Quốc gia: {last_err}")


def fetch_procedure_page(page_index: int, page_size: int, keyword: str = "") -> list[dict[str, Any]]:
    """Fetch a page of procedures from CSDL Quốc gia về TTHC."""
    params = {
        "type": "ref",
        "service": "procedure_advanced_search_service_v2",
        "keyword": keyword,
        "pageIndex": page_index,
        "pageSize": page_size,
        "is_online": -1,
    }
    data = post_dvc_rest(params)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("data", "items", "records", "list"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def fetch_procedure_detail(code: str) -> dict[str, Any]:
    """Fetch full procedure detail (steps, dossier, fees, legal basis) by procedure code."""
    params = {
        "type": "ref",
        "service": "procedure_detail_service_v2",
        "ma_thu_tuc": code,
    }
    try:
        data = post_dvc_rest(params)
        if isinstance(data, list) and data:
            return data[0] if isinstance(data[0], dict) else {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def extract_steps_from_text(trinh_tu: str) -> list[str]:
    """Split official 'Trình tự thực hiện' prose into concise step labels."""
    cleaned = clean_html_text(trinh_tu)
    if not cleaned:
        return [
            "Chuẩn bị hồ sơ theo quy định",
            "Nộp hồ sơ trực tuyến trên Cổng DVC Quốc gia hoặc trực tiếp",
            "Cơ quan có thẩm quyền tiếp nhận và thẩm định hồ sơ",
            "Nộp lệ phí (nếu có) và nhận kết quả giải quyết",
        ]
    # Try splitting on 'Bước 1', 'Bước 2', ...
    parts = re.split(r"(?i)(?=\bBước\s*\d+)", cleaned)
    steps = [p.strip(" -–:;\n") for p in parts if p.strip()]
    if len(steps) < 2:
        steps = [ln.strip(" -•+*") for ln in cleaned.splitlines() if len(ln.strip()) > 12][:6]
    return steps[:8]


def build_mermaid_flowchart(steps: list[str]) -> str:
    """Build a valid Mermaid flowchart TD diagram from extracted steps."""
    lines = ["flowchart TD"]
    for idx, step in enumerate(steps):
        node_id = f"S{idx + 1}"
        short = step.replace('"', "'").replace("\n", " ")
        if len(short) > 78:
            short = short[:75].rstrip() + "..."
        if not re.match(r"(?i)^bước\s*\d+", short):
            short = f"Bước {idx + 1}: {short}"
        if idx == 0:
            lines.append(f'    {node_id}["{short}"]')
        else:
            prev_id = f"S{idx}"
            lines.append(f'    {prev_id} --> {node_id}["{short}"]')
    return "\n".join(lines)


def yaml_escape(val: str) -> str:
    return str(val or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def build_markdown(item: dict[str, Any], detail: dict[str, Any]) -> tuple[str, str, str]:
    """Convert a DVC API record into (ministry_folder, filename, markdown_content)."""
    code = str(item.get("MA_THU_TUC") or item.get("PROCEDURE_CODE") or detail.get("MA_THU_TUC") or "").strip()
    title = str(item.get("TEN_THU_TUC") or item.get("PROCEDURE_NAME") or detail.get("TEN_THU_TUC") or "Thủ tục hành chính").strip()
    ministry = str(
        item.get("TEN_CO_QUAN_CONG_BO")
        or item.get("AGENCY_NAME")
        or detail.get("TEN_CO_QUAN_CONG_BO")
        or "Cơ quan Nhà nước"
    ).strip()
    sector = str(item.get("TEN_LINH_VUC") or detail.get("TEN_LINH_VUC") or "Hành chính công").strip()
    level = str(item.get("CAP_THUC_HIEN") or detail.get("CAP_THUC_HIEN") or "").strip()
    processing_time = clean_html_text(str(detail.get("THOI_HAN_GIAI_QUYET") or item.get("THOI_HAN_GIAI_QUYET") or "Xem chi tiết trên Cổng DVC"))
    fee = clean_html_text(str(detail.get("PHI_LE_PHI") or item.get("PHI_LE_PHI") or "Theo quy định hiện hành"))
    trinh_tu = str(detail.get("TRINH_TU_THUC_HIEN") or item.get("TRINH_TU_THUC_HIEN") or "")
    ho_so = clean_html_text(str(detail.get("THANH_PHAN_HO_SO") or item.get("THANH_PHAN_HO_SO") or "Xem chi tiết thành phần hồ sơ và tải biểu mẫu tại trang gốc."))

    official_url = DETAIL_URL_TPL.format(code=urllib.parse.quote(code)) if code else "https://vpcp.dichvucong.gov.vn/p/home/dvc-tthc-thu-tuc-hanh-chinh.html"
    slug = slugify(f"{title}-{code}" if code else title)[:90]
    ministry_folder = slugify(ministry)[:50] or "khac"

    steps = extract_steps_from_text(trinh_tu)
    mermaid = build_mermaid_flowchart(steps)
    steps_md = "\n".join(
        f"{i + 1}. **Bước {i + 1}**: {st}" for i, st in enumerate(steps)
    )
    summary = f"Thủ tục {title} thuộc lĩnh vực {sector} do {ministry} công bố (Mã TTHC: {code or 'N/A'})."
    tags = [t for t in [sector.lower(), ministry.lower(), code.lower()] if t]

    md = f"""---
slug: {slug}
code: "{yaml_escape(code)}"
title: "{yaml_escape(title)}"
ministry: "{yaml_escape(ministry)}"
sector: "{yaml_escape(sector)}"
level: "{yaml_escape(level)}"
online_level: "Tra cứu & Nộp trên Cổng DVC Quốc gia"
processing_time: "{yaml_escape(processing_time[:160])}"
fee: "{yaml_escape(fee[:160])}"
official_url: "{official_url}"
portal_url: "{official_url}"
portal_name: "Cổng Dịch vụ công Quốc gia"
tags: {json.dumps(tags, ensure_ascii=False)}
updated_at: "{date.today().isoformat()}"
summary: "{yaml_escape(summary)}"
---

# {title}

## Thông tin nhanh

| Hạng mục | Chi tiết |
|---|---|
| **Mã thủ tục** | `{code or "N/A"}` |
| **Cơ quan công bố** | {ministry} |
| **Lĩnh vực** | {sector} |
| **Cấp thực hiện** | {level or "Theo phân cấp"} |

## Sơ đồ quy trình

```mermaid
{mermaid}
```

## Các bước thực hiện ngắn gọn

{steps_md}

## Hồ sơ & biểu mẫu cần chuẩn bị

{ho_so}

## Liên kết trang gốc & nộp hồ sơ trực tuyến

- [Chi tiết thủ tục & tải biểu mẫu trên Cổng Dịch vụ công Quốc gia]({official_url})
"""
    return ministry_folder, f"{slug}.md", md


def main() -> None:
    parser = argparse.ArgumentParser(description="Thu thập thủ tục hành chính từ dichvucong.gov.vn sang file Markdown + Mermaid.")
    parser.add_argument("--keyword", default="", help="Từ khóa lọc (để trống để lấy tất cả)")
    parser.add_argument("--limit", type=int, default=50, help="Số thủ tục tối đa muốn lấy (bỏ qua nếu dùng --all)")
    parser.add_argument("--all", action="store_true", help="Quét toàn bộ thủ tục trên CSDL Quốc gia")
    parser.add_argument("--batch-size", type=int, default=50, help="Số bản ghi mỗi trang API")
    parser.add_argument("--delay", type=float, default=0.35, help="Thời gian nghỉ giữa các request (giây)")
    parser.add_argument("--out-dir", default=str(PROCEDURES_DIR / "imported"), help="Thư mục lưu file .md thu thập được")
    parser.add_argument("--sync", action="store_true", help="Tự động đồng bộ vào PostgreSQL/SQLite sau khi tải xong")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    max_items = 100_000 if args.all else args.limit

    page = 1
    saved = 0
    print(f"[CRAWL] Bắt đầu quét CSDL Quốc gia về TTHC (keyword='{args.keyword}', max={max_items})...")

    while saved < max_items:
        try:
            items = fetch_procedure_page(page_index=page, page_size=args.batch_size, keyword=args.keyword)
        except Exception as exc:
            print(f"[CRAWL] Dừng ở trang {page} do lỗi kết nối: {exc}")
            break

        if not items:
            print(f"[CRAWL] Đã hết dữ liệu ở trang {page}.")
            break

        for item in items:
            if saved >= max_items:
                break
            code = str(item.get("MA_THU_TUC") or item.get("PROCEDURE_CODE") or "").strip()
            detail = fetch_procedure_detail(code) if code else {}
            folder, filename, md_content = build_markdown(item, detail)
            target = out_dir / folder / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(md_content, encoding="utf-8")
            saved += 1
            if saved % 25 == 0:
                print(f"[CRAWL] Đã tạo {saved} file Markdown...")
            if args.delay > 0:
                time.sleep(args.delay)

        page += 1

    print(f"[CRAWL] Hoàn tất! Đã tạo {saved} file Markdown trong {out_dir}")

    if args.sync:
        repo = create_repository(DATABASE_URL)
        repo.init_schema()
        stats = sync_directory(repo, PROCEDURES_DIR)
        print(f"[SYNC] Đã đồng bộ vào {repo.engine_name}: {json.dumps(stats, ensure_ascii=False)}")
        print(f"[SYNC] Tổng số thủ tục trong database: {repo.count()}")


if __name__ == "__main__":
    main()
