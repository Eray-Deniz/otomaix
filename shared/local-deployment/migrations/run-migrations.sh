#!/bin/bash
# Tüm SQL migration'larını PostgreSQL'e uygular.
# setup.sh tarafından çağrılır; PostgreSQL'in çalışır durumda olması gerekir.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Docker Compose servisindeki PostgreSQL'e bağlan
PG_CMD="docker compose exec -T postgres psql -U otomaix -d otomaix"

# social schema'yı oluştur (idempotent)
$PG_CMD -c "CREATE SCHEMA IF NOT EXISTS social;" 2>/dev/null || true

# pgvector extension'ını etkinleştir
$PG_CMD -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true

# Migration'ları sırayla uygula
MIGRATIONS=(
    "001_initial_social.sql"
    "002_autoposting.sql"
    "003_social_account_unique.sql"
    "004_telegram_chat_id.sql"
    "005_telegram_bot_token.sql"
    "006_document_rag.sql"
    "007_competitor_analysis.sql"
    "008_trend_cache.sql"
    "009_subscriptions.sql"
    "010_trial_period.sql"
)

for MIGRATION in "${MIGRATIONS[@]}"; do
    FILE="$SCRIPT_DIR/$MIGRATION"
    if [ -f "$FILE" ]; then
        echo "  → $MIGRATION"
        $PG_CMD -f "/dev/stdin" < "$FILE"
    else
        echo "  ⚠  $MIGRATION bulunamadı, atlanıyor."
    fi
done

echo "  ✓ Tüm migration'lar uygulandı."
