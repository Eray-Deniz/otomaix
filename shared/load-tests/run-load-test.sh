#!/bin/bash
# Otomaix Load Test — Hızlı Başlatıcı
# Kullanım: ./run-load-test.sh [production|local|headless]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-interactive}"
HOST="${OTOMAIX_HOST:-https://api.otomaix.com}"
RESULTS_DIR="$SCRIPT_DIR/results"

mkdir -p "$RESULTS_DIR"

if [ -z "$OTOMAIX_JWT" ]; then
    echo "⚠  OTOMAIX_JWT boş — tam test için token gerekli."
    echo "   export OTOMAIX_JWT='<supabase_jwt_token>'"
fi

# venv içindeki locust'u kullan
VENV="$SCRIPT_DIR/.venv"
if [ ! -f "$VENV/bin/locust" ]; then
    echo "venv bulunamadı, oluşturuluyor..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install locust --quiet
fi
LOCUST="$VENV/bin/locust"

LOCUSTFILE="$SCRIPT_DIR/locustfile.py"

case "$MODE" in
    headless)
        echo "▶  Headless mod — 50 kullanıcı, 60 saniye, $HOST"
        "$LOCUST" -f "$LOCUSTFILE" \
               --host="$HOST" \
               --users=50 \
               --spawn-rate=5 \
               --run-time=60s \
               --headless \
               --csv="$RESULTS_DIR/load_test_$(date +%Y%m%d_%H%M%S)"
        echo "✓  Sonuçlar: $RESULTS_DIR/"
        ;;
    local)
        HOST="http://localhost:8000"
        echo "▶  Local mod — http://localhost:8000 → Locust UI: http://localhost:8089"
        "$LOCUST" -f "$LOCUSTFILE" --host="$HOST"
        ;;
    *)
        echo "▶  Interactive mod → Locust UI: http://localhost:8089"
        echo "   Hedef: $HOST"
        echo "   Önerilen: 50 kullanıcı, spawn rate 5"
        "$LOCUST" -f "$LOCUSTFILE" --host="$HOST"
        ;;
esac
