#!/usr/bin/env bash
# Phase 1 — Uçtan uca test scripti
# Kullanım: bash ~/otomaix/shared/test_phase1.sh

set -euo pipefail

API_URL="https://api.otomaix.com"
DB_HOST="127.0.0.1"
DB_PORT="5433"
DB_NAME="otomaix"
DB_USER="otomaix"
REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

PASS=0
FAIL=0

pass() { echo "  [PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }

echo ""
echo "======================================="
echo "  Otomaix Social — Phase 1 Test Suite  "
echo "======================================="
echo ""

# ── 1. Health check ──────────────────────────────────────────────────────────
echo "1. API Health Check"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL/health" || echo "000")
if [ "$STATUS" = "200" ]; then
  pass "$API_URL/health → HTTP 200"
else
  fail "$API_URL/health → HTTP $STATUS (beklenen: 200)"
fi

# ── 2. Swagger UI ─────────────────────────────────────────────────────────────
echo ""
echo "2. Swagger UI"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL/docs" || echo "000")
if [ "$STATUS" = "200" ]; then
  pass "$API_URL/docs → HTTP 200"
else
  fail "$API_URL/docs → HTTP $STATUS"
fi

# ── 3. PostgreSQL ─────────────────────────────────────────────────────────────
echo ""
echo "3. PostgreSQL Bağlantısı"
if command -v psql &>/dev/null; then
  if PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\q" &>/dev/null 2>&1; then
    pass "PostgreSQL bağlantısı başarılı ($DB_HOST:$DB_PORT/$DB_NAME)"
  else
    fail "PostgreSQL bağlantısı başarısız ($DB_HOST:$DB_PORT/$DB_NAME)"
  fi
else
  echo "  [SKIP] psql bulunamadı — PostgreSQL testi atlandı"
fi

# ── 4. PostgreSQL schema tabloları ───────────────────────────────────────────
echo ""
echo "4. PostgreSQL — social schema tabloları"
if command -v psql &>/dev/null; then
  TABLES=$(PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'social';" 2>/dev/null | tr -d ' ' || echo "0")
  EXPECTED=9
  if [ "$TABLES" -ge "$EXPECTED" ] 2>/dev/null; then
    pass "social schema'da $TABLES tablo bulundu (minimum $EXPECTED)"
  else
    fail "social schema'da $TABLES tablo bulundu (minimum $EXPECTED bekleniyor)"
  fi
else
  echo "  [SKIP] psql bulunamadı — schema testi atlandı"
fi

# ── 5. Redis ─────────────────────────────────────────────────────────────────
echo ""
echo "5. Redis Bağlantısı"
if command -v redis-cli &>/dev/null; then
  PONG=$(redis-cli -u "$REDIS_URL" ping 2>/dev/null || echo "")
  if [ "$PONG" = "PONG" ]; then
    pass "Redis PING → PONG"
  else
    fail "Redis PING → yanıt yok veya hata"
  fi
else
  echo "  [SKIP] redis-cli bulunamadı — Redis testi atlandı"
fi

# ── 6. R2 Storage ────────────────────────────────────────────────────────────
echo ""
echo "6. Cloudflare R2 — Presigned URL"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
  -X POST "$API_URL/storage/presigned-url" \
  -H "Content-Type: application/json" \
  -d '{"path":"test/health_check.txt","content_type":"text/plain"}' || echo "000")
if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "401" ]; then
  pass "R2 presigned-url endpoint erişilebilir (HTTP $RESPONSE)"
else
  fail "R2 presigned-url endpoint yanıt vermedi (HTTP $RESPONSE)"
fi

# ── 7. Frontend ───────────────────────────────────────────────────────────────
echo ""
echo "7. Frontend (app.otomaix.com)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://app.otomaix.com" || echo "000")
if [ "$STATUS" = "200" ] || [ "$STATUS" = "307" ] || [ "$STATUS" = "302" ]; then
  pass "app.otomaix.com → HTTP $STATUS"
else
  fail "app.otomaix.com → HTTP $STATUS"
fi

# ── 8. n8n ────────────────────────────────────────────────────────────────────
echo ""
echo "8. n8n"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://n8n.otomaix.com" || echo "000")
if [ "$STATUS" = "200" ] || [ "$STATUS" = "301" ] || [ "$STATUS" = "302" ]; then
  pass "n8n.otomaix.com → HTTP $STATUS"
else
  fail "n8n.otomaix.com → HTTP $STATUS"
fi

# ── Özet ─────────────────────────────────────────────────────────────────────
echo ""
echo "======================================="
echo "  SONUÇ: $PASS PASS / $FAIL FAIL"
echo "======================================="
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "  Tüm testler geçti. Phase 2'ye geçebilirsiniz!"
else
  echo "  $FAIL test başarısız. Yukarıdaki hataları düzeltin."
fi
echo ""
