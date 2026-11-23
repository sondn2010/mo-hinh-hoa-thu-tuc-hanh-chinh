#!/usr/bin/env bash
# Tự động cài đặt môi trường dev (nếu chưa có) và chạy site trên macOS / Linux.
# Cách dùng:
#   ./run_develop.sh
#   ./run_develop.sh --sqlite
#   ./run_develop.sh --port 8080
#   ./run_develop.sh --reinstall

set -euo pipefail

PORT=8000
LOCAL_SQLITE=false
REINSTALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sqlite) LOCAL_SQLITE=true; shift ;;
    --reinstall) REINSTALL=true; shift ;;
    --port) PORT="${2:-8000}"; shift 2 ;;
    *) echo "Tham số không hỗ trợ: $1"; exit 1 ;;
  esac
done

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  Hành chính Công VN - Khởi động môi trường Develop (macOS)"
echo "============================================================"

# 1. Tìm Python 3
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[LỖI] Không tìm thấy Python 3. Cài đặt bằng Homebrew: brew install python"
  exit 1
fi
echo "[1/5] Sử dụng Python: $($PYTHON_BIN --version)"

# 2. Tạo môi trường ảo .venv nếu chưa có
VENV_DIR="$PROJECT_ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "[2/5] Đang tạo môi trường ảo .venv ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "[2/5] Đã có môi trường ảo .venv."
fi

# 3. Cài đặt thư viện từ requirements.txt (chỉ chạy lại khi thay đổi hoặc --reinstall)
REQ_FILE="$PROJECT_ROOT/requirements.txt"
HASH_FILE="$VENV_DIR/.requirements.sha256"
if command -v shasum >/dev/null 2>&1; then
  CURRENT_HASH="$(shasum -a 256 "$REQ_FILE" | awk '{print $1}')"
else
  CURRENT_HASH="$(sha256sum "$REQ_FILE" | awk '{print $1}')"
fi
INSTALLED_HASH="$(cat "$HASH_FILE" 2>/dev/null || true)"

if [[ "$REINSTALL" == "true" || "$CURRENT_HASH" != "$INSTALLED_HASH" ]]; then
  echo "[3/5] Đang cài đặt thư viện Python từ requirements.txt ..."
  "$VENV_PYTHON" -m pip install --upgrade pip --quiet
  "$VENV_PYTHON" -m pip install -r "$REQ_FILE"
  printf '%s' "$CURRENT_HASH" > "$HASH_FILE"
else
  echo "[3/5] Thư viện Python đã đầy đủ."
fi

# 4. Cấu hình .env và Database (ưu tiên PostgreSQL qua Docker, tự động fallback SQLite nếu chưa bật Docker)
if [[ ! -f "$PROJECT_ROOT/.env" && -f "$PROJECT_ROOT/.env.example" ]]; then
  cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
fi

if [[ -z "${DATABASE_URL:-}" && -f "$PROJECT_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
fi

if [[ "$LOCAL_SQLITE" == "true" ]]; then
  export DATABASE_URL="sqlite:///./dvc_local.db"
  echo "[4/5] Chế độ nhanh (--sqlite): Sử dụng SQLite cục bộ (dvc_local.db)."
else
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo "[4/5] Đang khởi động PostgreSQL 16 bằng Docker Compose ..."
    docker compose up -d postgres
    echo "      Đang chờ PostgreSQL sẵn sàng..."
    for _ in $(seq 1 20); do
      if docker compose exec -T postgres pg_isready -U dvc_user -d dvc_vietnam >/dev/null 2>&1; then
        break
      fi
      sleep 1
    done
    export DATABASE_URL="${DATABASE_URL:-postgresql://dvc_user:dvc_secret_2026@localhost:5432/dvc_vietnam}"
    echo "      PostgreSQL đã sẵn sàng: $DATABASE_URL"
  else
    echo "[4/5] Không phát hiện Docker đang chạy -> Tự động chuyển sang SQLite cục bộ (dvc_local.db)."
    echo "      (Bật Docker Desktop/OrbStack rồi chạy lại ./run_develop.sh để dùng PostgreSQL 16)"
    export DATABASE_URL="sqlite:///./dvc_local.db"
  fi
fi

# 5. Đồng bộ thư mục procedures/*.md & chạy Uvicorn
echo "[5/5] Đồng bộ thư mục procedures/*.md và khởi chạy server..."
"$VENV_PYTHON" scripts/sync_md.py

echo ""
echo "  Website đang chạy tại : http://127.0.0.1:$PORT"
echo "  Trang cập nhật .md    : http://127.0.0.1:$PORT/cap-nhat"
echo "  Nhấn Ctrl+C để dừng server."
echo ""

exec "$VENV_PYTHON" -m uvicorn app.main:app --reload --host 127.0.0.1 --port "$PORT"