/**
 * md_reviewer.js — Interactive Markdown + YAML Frontmatter + Mermaid Reviewer
 * Designed for reviewing Vietnamese Public Administrative Procedure (.md) files.
 */
(function () {
  "use strict";

  const SAMPLES = {
    ho_chieu: `---
slug: cap-ho-chieu-pho-thong
code: "1.001456"
title: "Cấp hộ chiếu phổ thông ở trong nước"
ministry: "Bộ Công an"
sector: "Xuất nhập cảnh"
level: "Cấp Tỉnh / Cấp Trung ương"
online_level: "Toàn trình (VNeID mức 2)"
processing_time: "08 ngày làm việc (cấp tỉnh) / 05 ngày làm việc (cấp trung ương)"
fee: "Theo biểu mức lệ phí xuất nhập cảnh (nộp trực tuyến qua Cổng DVC)"
official_url: "https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001456"
portal_url: "https://dichvucong.bocongan.gov.vn"
portal_name: "Cổng Dịch vụ công Bộ Công an"
tags: ["hộ chiếu", "passport", "xuất nhập cảnh", "vneid", "bộ công an"]
updated_at: "2026-11-23"
summary: "Nộp hồ sơ cấp hộ chiếu phổ thông gắn chip hoặc không gắn chip hoàn toàn trực tuyến qua Cổng DVC Bộ Công an và VNeID mức 2."
---

# Cấp hộ chiếu phổ thông ở trong nước

## Thông tin nhanh

| Hạng mục | Chi tiết |
|---|---|
| **Mã thủ tục** | \`1.001456\` (Cấp tỉnh) / \`1.001471\` (Cấp trung ương) |
| **Cơ quan thực hiện** | Phòng Quản lý xuất nhập cảnh Công an cấp tỉnh / Cục QLXNC |
| **Hình thức nộp** | Trực tuyến toàn trình qua VNeID mức 2 hoặc trực tiếp |

## Sơ đồ quy trình

\`\`\`mermaid
flowchart TD
    A["Bước 1: Chuẩn bị ảnh 4x6 nền trắng & VNeID mức 2"] --> B["Bước 2: Đăng nhập Cổng DVC Bộ Công an / VNeID"]
    B --> C["Bước 3: Chọn 'Cấp hộ chiếu phổ thông' & tải ảnh"]
    C --> D["Bước 4: Kiểm tra thông tin & chọn nơi nhận"]
    D --> E["Bước 5: Thanh toán lệ phí qua đường dẫn chính thức"]
    E --> F["Bước 6: Cơ quan QLXNC xét duyệt & in hộ chiếu"]
    F --> G["Bước 7: Nhận hộ chiếu trực tiếp hoặc qua bưu điện"]
\`\`\`

## Các bước thực hiện ngắn gọn

1. **Bước 1 — Chuẩn bị ảnh & tài khoản**: Cần tài khoản **VNeID mức độ 2** và ảnh chân dung 4x6cm nền trắng, định dạng \`.jpg\`.
2. **Bước 2 — Đăng nhập Cổng DVC**: Truy cập [Cổng Dịch vụ công Bộ Công an](https://dichvucong.bocongan.gov.vn) hoặc VNeID → chọn **Cấp hộ chiếu phổ thông ở trong nước**.
3. **Bước 3 — Khai tờ khai điện tử**: Tải ảnh chân dung, kiểm tra thông tin tự động điền từ CSDL dân cư và chọn hình thức nhận kết quả.
4. **Bước 4 — Thanh toán lệ phí trực tuyến**: Thanh toán theo đường dẫn chính thức gửi qua tin nhắn/email sau khi cán bộ duyệt hồ sơ.
5. **Bước 5 — Nhận hộ chiếu**: Theo dõi tiến độ bằng mã hồ sơ và nhận tại Phòng QLXNC hoặc qua bưu điện.

## Hồ sơ & biểu mẫu cần chuẩn bị

- **Tờ khai đề nghị cấp hộ chiếu phổ thông** (khai trực tuyến trên Cổng DVC).
- **Ảnh chân dung 4x6cm nền trắng** (chụp không quá 06 tháng).
- **Hộ chiếu phổ thông cấp lần gần nhất** (nếu còn giá trị sử dụng).

## Liên kết trang gốc & nộp hồ sơ trực tuyến

- [Chi tiết thủ tục trên Cổng Dịch vụ công Quốc gia (1.001456)](https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001456)
- [Nộp hồ sơ trực tuyến tại Cổng Dịch vụ công Bộ Công an](https://dichvucong.bocongan.gov.vn)
`,

    khai_sinh: `---
slug: dang-ky-khai-sinh-lien-thong
code: "1.001193"
title: "Đăng ký khai sinh (và Liên thông Khai sinh - Thường trú - Thẻ BHYT)"
ministry: "Bộ Tư pháp"
sector: "Hộ tịch & Tư pháp"
level: "Cấp Xã"
online_level: "Toàn trình (Dịch vụ công liên thông)"
processing_time: "Ngay trong ngày làm việc (khai sinh đơn lẻ)"
fee: "Miễn lệ phí đăng ký khai sinh đúng hạn"
official_url: "https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-dung-chung.html?ma_thu_tuc=1.001193"
portal_url: "https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-hanh-chinh.html?ma_thu_tuc=2.002621"
portal_name: "Cổng Dịch vụ công Quốc gia (Nhóm liên thông)"
tags: ["khai sinh", "liên thông", "bhyt trẻ em", "hộ tịch", "bộ tư pháp"]
updated_at: "2026-11-23"
summary: "Thực hiện 1 lần khai báo trực tuyến để nhận đồng thời Giấy khai sinh, Đăng ký thường trú và Thẻ bảo hiểm y tế cho trẻ dưới 6 tuổi."
---

# Đăng ký khai sinh (và Liên thông Khai sinh - Thường trú - Thẻ BHYT)

## Sơ đồ quy trình

\`\`\`mermaid
flowchart TD
    A["Bước 1: Chuẩn bị Giấy chứng sinh & Giấy CN kết hôn"] --> B["Bước 2: Đăng nhập Cổng DVC Quốc gia (VNeID)"]
    B --> C["Bước 3: Điền 01 Tờ khai điện tử liên thông"]
    C --> D["Bước 4: UBND cấp xã cấp Giấy khai sinh"]
    D --> E["Bước 5a: Tự động chuyển Công an đăng ký thường trú"]
    D --> F["Bước 5b: Tự động chuyển BHXH cấp thẻ BHYT trẻ em"]
    E --> G["Bước 6: Nhận bản điện tử & bản giấy theo đăng ký"]
    F --> G
\`\`\`

## Các bước thực hiện ngắn gọn

1. **Bước 1 — Chuẩn bị giấy tờ**: Chụp/scan rõ nét **Giấy chứng sinh** do bệnh viện cấp và thông tin Giấy chứng nhận kết hôn.
2. **Bước 2 — Nộp 01 hồ sơ liên thông**: Đăng nhập [Cổng Dịch vụ công Quốc gia](https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-hanh-chinh.html?ma_thu_tuc=2.002621) bằng VNeID và chọn nhóm thủ tục liên thông.
3. **Bước 3 — Cấp Giấy khai sinh**: Công chức Tư pháp - Hộ tịch cấp xã giải quyết ngay trong ngày (sau 15h trả ngày làm việc tiếp theo).
4. **Bước 4 — Liên thông tự động**: Hệ thống tự động chuyển dữ liệu sang Công an cấp xã và cơ quan BHXH.
5. **Bước 5 — Nhận kết quả**: Nhận bản điện tử trên Cổng DVC/VNeID và bản giấy tại Trung tâm Phục vụ HCC hoặc qua bưu điện.

## Liên kết trang gốc

- [Thủ tục đăng ký khai sinh (1.001193)](https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-dung-chung.html?ma_thu_tuc=1.001193)
- [Liên thông Khai sinh - Thường trú - BHYT (2.002621)](https://vpcp.dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-hanh-chinh.html?ma_thu_tuc=2.002621)
`,

    template: `---
slug: ten-thu-tuc-khong-dau
code: "MA-THU-TUC"
title: "Tên thủ tục hành chính mới"
ministry: "Tên Bộ / Cơ quan chủ quản"
sector: "Lĩnh vực (VD: Cư trú, Tư pháp, Thuế...)"
level: "Cấp thực hiện (Cấp Tỉnh / Cấp Xã)"
online_level: "Toàn trình / Một phần"
processing_time: "05 ngày làm việc"
fee: "Miễn lệ phí"
official_url: "https://dichvucong.gov.vn"
portal_url: "https://dichvucong.gov.vn"
portal_name: "Cổng Dịch vụ công Quốc gia"
tags: ["từ khóa 1", "từ khóa 2"]
updated_at: "2026-11-23"
summary: "Tóm tắt ngắn gọn 1-2 câu về mục đích và kết quả của thủ tục."
---

# Tên thủ tục hành chính mới

## Sơ đồ quy trình

\`\`\`mermaid
flowchart TD
    A["Bước 1: Chuẩn bị hồ sơ"] --> B["Bước 2: Nộp hồ sơ trực tuyến trên Cổng DVC"]
    B --> C{"Cơ quan thẩm định hồ sơ"}
    C -->|"Thiếu"| D["Bổ sung hồ sơ"]
    D --> B
    C -->|"Hợp lệ"| E["Bước 3: Nộp lệ phí (nếu có) & nhận kết quả"]
\`\`\`

## Các bước thực hiện ngắn gọn

1. **Bước 1 — Chuẩn bị hồ sơ**: Mô tả ngắn gọn giấy tờ cần thiết.
2. **Bước 2 — Nộp hồ sơ**: Hướng dẫn truy cập cổng dịch vụ công.
3. **Bước 3 — Nhận kết quả**: Thời gian và cách thức nhận kết quả.

## Hồ sơ & biểu mẫu cần chuẩn bị

- Giấy tờ 1 (Mẫu số ...)
- Giấy tờ 2
`
  };

  function stripAccents(str) {
    return (str || "")
      .replace(/đ/g, "d")
      .replace(/Đ/g, "D")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /** Lightweight YAML Frontmatter parser (handles strings, quoted values, and inline arrays). */
  function parseFrontmatter(raw) {
    const cleaned = raw.replace(/^\uFEFF/, "");
    const match = cleaned.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?([\s\S]*)$/);
    if (!match) {
      return { meta: {}, body: cleaned };
    }
    const meta = {};
    const lines = match[1].split(/\r?\n/);
    for (const line of lines) {
      const m = line.match(/^\s*([A-Za-z0-9_]+)\s*:\s*(.*)\s*$/);
      if (!m) continue;
      const key = m[1];
      let val = m[2].trim();
      if (val.startsWith("[") && val.endsWith("]")) {
        meta[key] = val
          .slice(1, -1)
          .split(",")
          .map((s) => s.trim().replace(/^["']|["']$/g, ""))
          .filter(Boolean);
      } else {
        meta[key] = val.replace(/^["']|["']$/g, "");
      }
    }
    return { meta, body: match[2] };
  }

  function extractMermaid(body) {
    const m = body.match(/```mermaid\s*\r?\n([\s\S]*?)```/i);
    return m ? m[1].trim() : "";
  }

  function extractSteps(body) {
    const steps = [];
    let inSteps = false;
    for (const line of body.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (trimmed.startsWith("## ")) {
        const plain = stripAccents(trimmed).toLowerCase();
        inSteps = plain.includes("cac buoc") || plain.includes("trinh tu");
        continue;
      }
      if (inSteps) {
        const m = line.match(/^\s*\d+\.\s+\*\*(.+?)\*\*\s*(?:[—–:\-]\s*)?(.*)$/);
        if (m) {
          steps.push({
            index: steps.length + 1,
            title: m[1].trim(),
            desc: m[2].trim()
          });
        }
      }
    }
    return steps;
  }

  function stripMermaidAndH1(body) {
    return body
      .replace(/```mermaid\s*\r?\n[\s\S]*?```/gi, "")
      .replace(/^\s*#\s+.+?\r?\n+/, "")
      .replace(/##\s+Sơ đồ quy trình\s*\r?\n+(?=##|$)/i, "");
  }

  function copyText(text, onDone) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(onDone).catch(() => fallbackCopy(text, onDone));
    } else {
      fallbackCopy(text, onDone);
    }
  }

  function fallbackCopy(text, onDone) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
    } catch (_err) {
      // ignore
    }
    document.body.removeChild(ta);
    if (onDone) onDone();
  }

  function initReviewer() {
    const editor = document.getElementById("mdEditor");
    const fileInput = document.getElementById("mdFileInput");
    const openFileBtn = document.getElementById("openFileBtn");
    const sampleSelect = document.getElementById("sampleSelect");
    const fileNameBadge = document.getElementById("fileNameBadge");
    const downloadBtn = document.getElementById("downloadBtn");
    const copyMdBtn = document.getElementById("copyMdBtn");
    const modeButtons = document.querySelectorAll("[data-view-mode]");
    const workspace = document.getElementById("workspaceGrid");
    const editorPane = document.getElementById("editorPane");
    const previewPane = document.getElementById("previewPane");
    const dropOverlay = document.getElementById("dropOverlay");

    const validationBar = document.getElementById("validationBar");
    const previewHeader = document.getElementById("previewHeader");
    const stepsSection = document.getElementById("stepsSection");
    const stepsList = document.getElementById("stepsList");
    const mermaidSection = document.getElementById("mermaidSection");
    const mermaidRender = document.getElementById("mermaidRender");
    const mermaidError = document.getElementById("mermaidError");
    const markdownPreview = document.getElementById("markdownPreview");
    const toastEl = document.getElementById("toast");

    const zoomOutBtn = document.getElementById("zoomOutBtn");
    const zoomResetBtn = document.getElementById("zoomResetBtn");
    const zoomInBtn = document.getElementById("zoomInBtn");
    const copyMermaidBtn = document.getElementById("copyMermaidBtn");

    let currentScale = 1;
    let currentMermaidCode = "";
    let currentSlug = "thu-tuc";
    let renderCounter = 0;
    let debounceTimer = null;
    let toastTimer = null;

    if (window.mermaid) {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: "base",
        securityLevel: "loose",
        flowchart: { curve: "basis", htmlLabels: true, padding: 14 },
        themeVariables: {
          fontFamily: "Plus Jakarta Sans, Be Vietnam Pro, sans-serif",
          primaryColor: "#eff6ff",
          primaryTextColor: "#0f172a",
          primaryBorderColor: "#1d4ed8",
          lineColor: "#475569",
          secondaryColor: "#f0fdf4",
          tertiaryColor: "#fefce8"
        }
      });
    }

    function showToast(msg) {
      if (!toastEl) return;
      toastEl.textContent = msg;
      toastEl.classList.remove("opacity-0", "pointer-events-none");
      toastEl.classList.add("opacity-100");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {
        toastEl.classList.add("opacity-0", "pointer-events-none");
        toastEl.classList.remove("opacity-100");
      }, 2200);
    }

    function applyZoom() {
      if (mermaidRender) {
        mermaidRender.style.transform = `scale(${currentScale})`;
      }
      if (zoomResetBtn) {
        zoomResetBtn.textContent = `${Math.round(currentScale * 100)}%`;
      }
    }

    async function renderMermaidDiagram(code) {
      currentMermaidCode = code;
      if (!code) {
        mermaidSection.classList.add("hidden");
        return;
      }
      mermaidSection.classList.remove("hidden");
      mermaidError.classList.add("hidden");

      if (!window.mermaid) {
        mermaidRender.innerHTML = `<pre class="text-left text-xs p-3 bg-slate-100 rounded-lg overflow-auto">${escapeHtml(code)}</pre>`;
        return;
      }

      renderCounter += 1;
      const diagramId = `mmd_preview_${renderCounter}`;
      try {
        const result = await window.mermaid.render(diagramId, code);
        mermaidRender.innerHTML = result.svg;
        applyZoom();
      } catch (err) {
        mermaidError.textContent = `Mermaid syntax error: ${err && err.message ? err.message : String(err)}`;
        mermaidError.classList.remove("hidden");
      }
    }

    function renderValidation(meta, mermaidCode, steps) {
      const checks = [
        { label: "slug", ok: Boolean(meta.slug) },
        { label: "code", ok: Boolean(meta.code) },
        { label: "title", ok: Boolean(meta.title) },
        { label: "ministry", ok: Boolean(meta.ministry) },
        { label: "official_url", ok: /^https?:\/\//.test(meta.official_url || "") },
        { label: "mermaid", ok: Boolean(mermaidCode) },
        { label: `steps (${steps.length})`, ok: steps.length > 0 }
      ];
      const passed = checks.filter((c) => c.ok).length;
      const summaryColor = passed === checks.length ? "text-emerald-700 bg-emerald-50 border-emerald-200" : "text-amber-700 bg-amber-50 border-amber-200";
      const pills = checks
        .map(
          (c) =>
            `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${
              c.ok
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : "bg-amber-50 text-amber-800 border-amber-200"
            }">${c.ok ? "✓" : "!"} ${escapeHtml(c.label)}</span>`
        )
        .join("");

      validationBar.innerHTML = `
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${summaryColor}">
          Schema ${passed}/${checks.length}
        </span>
        ${pills}
      `;
    }

    function renderHeader(meta, body) {
      const h1Match = body.match(/^\s*#\s+(.+)$/m);
      const title = meta.title || (h1Match ? h1Match[1].trim() : "Untitled Procedure");
      currentSlug = meta.slug || "thu-tuc";

      const portalUrl = meta.portal_url || meta.official_url || "";
      const officialUrl = meta.official_url || "";

      const ctas = [];
      if (portalUrl) {
        ctas.push(
          `<a href="${escapeHtml(portalUrl)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold transition">
            Nộp trực tuyến (${escapeHtml(meta.portal_name || "Cổng DVC")}) ↗
          </a>`
        );
      }
      if (officialUrl && officialUrl !== portalUrl) {
        ctas.push(
          `<a href="${escapeHtml(officialUrl)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 text-sm font-semibold transition">
            Trang gốc & Biểu mẫu ↗
          </a>`
        );
      }

      previewHeader.innerHTML = `
        <div class="flex flex-wrap items-center gap-2 mb-2">
          ${meta.ministry ? `<span class="px-2.5 py-0.5 rounded-md text-xs font-bold bg-blue-50 text-blue-700">${escapeHtml(meta.ministry)}</span>` : ""}
          ${meta.sector ? `<span class="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-teal-50 text-teal-700">${escapeHtml(meta.sector)}</span>` : ""}
          ${meta.code ? `<span class="px-2 py-0.5 rounded-md text-xs font-mono bg-slate-100 text-slate-600">Mã: ${escapeHtml(meta.code)}</span>` : ""}
        </div>
        <h2 class="text-xl sm:text-2xl font-bold text-slate-900 leading-snug mb-1.5" style="font-family: 'Be Vietnam Pro', sans-serif;">${escapeHtml(title)}</h2>
        ${meta.summary ? `<p class="text-sm text-slate-600 mb-3">${escapeHtml(meta.summary)}</p>` : ""}
        ${ctas.length ? `<div class="flex flex-wrap gap-2 mb-3">${ctas.join("")}</div>` : ""}
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-3 border-t border-slate-200 text-xs">
          <div class="bg-slate-50 rounded-lg p-2.5"><span class="block text-slate-500">Thời hạn</span><strong class="text-slate-800">${escapeHtml(meta.processing_time || "—")}</strong></div>
          <div class="bg-slate-50 rounded-lg p-2.5"><span class="block text-slate-500">Mức độ trực tuyến</span><strong class="text-slate-800">${escapeHtml(meta.online_level || "—")}</strong></div>
          <div class="bg-slate-50 rounded-lg p-2.5"><span class="block text-slate-500">Lệ phí</span><strong class="text-slate-800">${escapeHtml(meta.fee || "—")}</strong></div>
        </div>
      `;
    }

    function renderSteps(steps) {
      if (!steps.length) {
        stepsSection.classList.add("hidden");
        return;
      }
      stepsSection.classList.remove("hidden");
      stepsList.innerHTML = steps
        .map((s) => {
          const descHtml = window.marked
            ? window.marked.parseInline(s.desc).replace(/<a href="(https?:\/\/[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-700 underline"')
            : escapeHtml(s.desc)
                .replace(/\*\*(.+?)\*\*/g, '<strong class="text-slate-900">$1</strong>')
                .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-slate-200/70 rounded text-xs">$1</code>')
                .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-700 underline">$1</a>');
          return `
            <li class="flex gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span class="w-7 h-7 rounded-full bg-blue-700 text-white text-xs font-bold grid place-items-center shrink-0 mt-0.5">${s.index}</span>
              <div class="min-w-0">
                <h4 class="text-sm font-bold text-slate-900">${escapeHtml(s.title)}</h4>
                <p class="text-sm text-slate-600 mt-0.5">${descHtml}</p>
              </div>
            </li>
          `;
        })
        .join("");
    }

    function renderMarkdownBody(body) {
      const cleaned = stripMermaidAndH1(body);
      if (window.marked) {
        let html = window.marked.parse(cleaned, { gfm: true, breaks: true });
        html = html.replace(/<a href="(https?:\/\/[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener noreferrer"');
        markdownPreview.innerHTML = html;
      } else {
        markdownPreview.innerHTML = `<pre class="whitespace-pre-wrap text-sm">${escapeHtml(cleaned)}</pre>`;
      }
    }

    function renderAll() {
      const raw = editor.value || "";
      const { meta, body } = parseFrontmatter(raw);
      const mermaidCode = extractMermaid(body);
      const steps = extractSteps(body);

      renderValidation(meta, mermaidCode, steps);
      renderHeader(meta, body);
      renderSteps(steps);
      renderMermaidDiagram(mermaidCode);
      renderMarkdownBody(body);

      try {
        localStorage.setItem("vn_md_reviewer_draft", raw);
      } catch (_e) {
        // ignore sandbox storage restrictions
      }
    }

    function scheduleRender() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(renderAll, 160);
    }

    function loadFile(file) {
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        editor.value = String(e.target.result || "");
        if (fileNameBadge) fileNameBadge.textContent = file.name;
        renderAll();
        showToast(`Loaded ${file.name}`);
      };
      reader.readAsText(file, "utf-8");
    }

    // Event Listeners
    editor.addEventListener("input", scheduleRender);

    openFileBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        loadFile(e.target.files[0]);
        e.target.value = "";
      }
    });

    sampleSelect.addEventListener("change", (e) => {
      const key = e.target.value;
      if (SAMPLES[key]) {
        editor.value = SAMPLES[key];
        if (fileNameBadge) fileNameBadge.textContent = `${key}.md`;
        renderAll();
        showToast("Loaded sample procedure");
      }
    });

    downloadBtn.addEventListener("click", () => {
      const blob = new Blob([editor.value || ""], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${currentSlug || "thu-tuc"}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast(`Downloaded ${currentSlug || "thu-tuc"}.md`);
    });

    copyMdBtn.addEventListener("click", () => {
      copyText(editor.value || "", () => showToast("Copied Markdown source"));
    });

    zoomOutBtn.addEventListener("click", () => {
      currentScale = Math.max(0.55, Number((currentScale - 0.15).toFixed(2)));
      applyZoom();
    });

    zoomResetBtn.addEventListener("click", () => {
      currentScale = 1;
      applyZoom();
    });

    zoomInBtn.addEventListener("click", () => {
      currentScale = Math.min(2.0, Number((currentScale + 0.15).toFixed(2)));
      applyZoom();
    });

    copyMermaidBtn.addEventListener("click", () => {
      if (!currentMermaidCode) return;
      copyText(currentMermaidCode, () => showToast("Copied Mermaid diagram code"));
    });

    // View mode switching (Split / Preview / Editor)
    modeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.getAttribute("data-view-mode");
        modeButtons.forEach((b) => {
          const active = b === btn;
          b.classList.toggle("bg-blue-700", active);
          b.classList.toggle("text-white", active);
          b.classList.toggle("text-slate-600", !active);
          b.classList.toggle("hover:bg-slate-100", !active);
        });
        if (mode === "split") {
          workspace.classList.add("lg:grid-cols-2");
          editorPane.classList.remove("hidden");
          previewPane.classList.remove("hidden");
        } else if (mode === "preview") {
          workspace.classList.remove("lg:grid-cols-2");
          editorPane.classList.add("hidden");
          previewPane.classList.remove("hidden");
        } else {
          workspace.classList.remove("lg:grid-cols-2");
          editorPane.classList.remove("hidden");
          previewPane.classList.add("hidden");
        }
      });
    });

    // Drag & Drop .md files anywhere on window
    let dragDepth = 0;
    window.addEventListener("dragenter", (e) => {
      e.preventDefault();
      dragDepth += 1;
      if (dropOverlay) dropOverlay.classList.remove("hidden");
    });
    window.addEventListener("dragover", (e) => e.preventDefault());
    window.addEventListener("dragleave", () => {
      dragDepth = Math.max(0, dragDepth - 1);
      if (dragDepth === 0 && dropOverlay) dropOverlay.classList.add("hidden");
    });
    window.addEventListener("drop", (e) => {
      e.preventDefault();
      dragDepth = 0;
      if (dropOverlay) dropOverlay.classList.add("hidden");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        loadFile(e.dataTransfer.files[0]);
      }
    });

    // Accessible '?' help tooltips
    document.addEventListener("click", (e) => {
      const tip = e.target.closest(".help-tip");
      document.querySelectorAll(".help-tip.open").forEach((el) => {
        if (el !== tip) el.classList.remove("open");
      });
      if (tip) {
        e.preventDefault();
        tip.classList.toggle("open");
      }
    });

    // Initial load: restore saved draft or load default sample
    let initialMd = SAMPLES.ho_chieu;
    try {
      const saved = localStorage.getItem("vn_md_reviewer_draft");
      if (saved && saved.trim()) initialMd = saved;
    } catch (_e) {
      // ignore
    }
    editor.value = initialMd;
    renderAll();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initReviewer);
  } else {
    initReviewer();
  }
})();