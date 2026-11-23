"""End-to-end automated tests for the Vietnamese Public Administrative Procedures portal."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.config import PROCEDURES_DIR
from app.main import create_app


def run_all_tests() -> None:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        tmp_path = Path(tmp)
        proc_copy = tmp_path / "procedures"
        shutil.copytree(PROCEDURES_DIR, proc_copy)
        db_url = f"sqlite:///{tmp_path / 'test.db'}"

        app = create_app(database_url=db_url, procedures_dir=proc_copy)
        with TestClient(app) as client:
            # 1. Home page renders and lists all 30 official procedures
            resp = client.get("/")
            assert resp.status_code == 200
            assert "Hành chính Công VN" in resp.text
            assert "Cấp thẻ Căn cước" in resp.text
            assert "Tách thửa hoặc hợp thửa đất" in resp.text

            r_all = client.get("/api/procedures", params={"limit": 100})
            assert r_all.status_code == 200
            assert r_all.json()["count"] == 30, f"Expected 30 procedures, got {r_all.json()['count']}"

            # 2. API search works with Vietnamese accents AND without accents
            r_accent = client.get("/api/procedures", params={"q": "hộ chiếu"})
            assert r_accent.status_code == 200
            assert r_accent.json()["items"][0]["slug"] == "cap-ho-chieu-pho-thong"

            r_no_accent = client.get("/api/procedures", params={"q": "ho chieu"})
            assert r_no_accent.status_code == 200
            assert r_no_accent.json()["items"][0]["slug"] == "cap-ho-chieu-pho-thong"

            # 3. Search newly added procedures (thất nghiệp, nhãn hiệu, hải quan, điện)
            for query, expected_slug in [
                ("that nghiep", "huong-tro-cap-that-nghiep"),
                ("nhan hieu", "dang-ky-nhan-hieu"),
                ("hai quan", "thu-tuc-hai-quan-nhap-khau"),
                ("cap dien moi", "cap-dien-moi-luoi-dien-ha-ap"),
                ("1.002809", "doi-giay-phep-lai-xe"),
            ]:
                r = client.get("/api/procedures", params={"q": query})
                assert r.status_code == 200
                slugs = [i["slug"] for i in r.json()["items"]]
                assert expected_slug in slugs, f"Expected {expected_slug} for query '{query}', got {slugs}"

            # 4. Ministry filter
            r_min = client.get("/api/procedures", params={"ministry": "Bộ Công an"})
            assert r_min.status_code == 200
            assert r_min.json()["count"] == 8

            # 5. Detail page renders Mermaid diagram, steps, and official links
            r_detail = client.get("/thu-tuc/tach-thua-hop-thua-dat")
            assert r_detail.status_code == 200
            assert "flowchart TD" in r_detail.text
            assert "1.012784" in r_detail.text
            assert "Bước 1" in r_detail.text

            # 6. Open MD upload via API adds a new procedure live
            new_md = """---
slug: thu-tuc-bo-sung-test
code: "TEST-001"
title: "Thủ tục kiểm thử bổ sung"
ministry: "Bộ Công an"
sector: "Kiểm thử"
processing_time: "01 ngày làm việc"
official_url: "https://dichvucong.bocongan.gov.vn"
portal_url: "https://dichvucong.bocongan.gov.vn"
portal_name: "Cổng DVC Bộ Công an"
tags: ["kiem thu"]
summary: "Thủ tục kiểm thử nạp mở."
---

# Thủ tục kiểm thử bổ sung

```mermaid
flowchart TD
    A["Bước 1: Nộp hồ sơ"] --> B["Bước 2: Nhận kết quả"]
```

## Các bước thực hiện ngắn gọn

1. **Bước 1 — Nộp hồ sơ**: Nộp trực tuyến.
2. **Bước 2 — Nhận kết quả**: Theo dõi trên Cổng DVC.
"""
            r_up = client.post(
                "/api/upload",
                files={"file": ("thu-tuc-bo-sung-test.md", new_md.encode("utf-8"), "text/markdown")},
                data={"subfolder": "bo-cong-an"},
            )
            assert r_up.status_code == 201
            assert r_up.json()["slug"] == "thu-tuc-bo-sung-test"

            # 7. Sync endpoint is idempotent
            r_sync = client.post("/api/sync")
            assert r_sync.status_code == 200
            assert r_sync.json()["scanned"] == 31
            assert r_sync.json()["unchanged"] == 31

            # 8. Template download works
            r_tpl = client.get("/api/template")
            assert r_tpl.status_code == 200
            assert "flowchart TD" in r_tpl.text

    print("ALL END-TO-END TESTS PASSED SUCCESSFULLY (30 official procedures verified)!")


if __name__ == "__main__":
    run_all_tests()
