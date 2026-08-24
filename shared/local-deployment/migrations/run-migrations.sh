#!/bin/bash
# Tüm SQL migration'larını PostgreSQL'e uygular.
# setup.sh tarafından çağrılır; PostgreSQL'in çalışır durumda olması gerekir.
#
# Bağlayıcı sözleşme (plan Task 3):
#
#   1. KANONİK KAYNAK = <repo kökü>/shared/db/migrations. Dosya listesi elle
#      TUTULMAZ, glob'lanır: elle yazılmış liste bayatlar (bu script 001–011'de
#      kalmıştı, o sırada kanonik dizinde 032 dosya vardı) ve eksik migration
#      sessizce atlanır. Bu dizinin yanındaki `shared/local-deployment/migrations`
#      kopyaları KAYNAK DEĞİLDİR — bayat kalıntıdır, kaldırılmaları ayrı temizlik.
#      Dizin yoksa script DURur: sessizce eski kopyaya düşmez.
#   2. `docker compose` çağrısı AÇIK `-f` ile yapılır — cwd'ye bağlı davranış yok
#      (setup.sh onu `shared/local-deployment` içinden, elle koşum repo kökünden
#      çağırabilir).
#   3. Her psql çağrısı `-v ON_ERROR_STOP=1` taşır. Bayrak olmadan psql hatayı
#      basar ama SIFIR döner; `set -e` de zinciri kesmez ve kısmi şema
#      "başarılı" raporlanır. Bayrakla ilk hata zinciri durdurur.
#
# NOT: migration'lar dosya BAŞINA tek transaction'a SARILMAZ — 011 `CREATE INDEX
# CONCURRENTLY` içerir ve transaction bloğunda koşamaz. Atomiklik gerektiren
# migration kendi `BEGIN/COMMIT`ini taşır (bugün yalnız 017 taşıyor).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DEPLOY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$LOCAL_DEPLOY_DIR/../.." && pwd)"

MIGRATIONS_DIR="$REPO_ROOT/shared/db/migrations"
COMPOSE_FILE="$LOCAL_DEPLOY_DIR/docker-compose.yml"

if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "  ✗ Kanonik migration dizini yok: $MIGRATIONS_DIR" >&2
    echo "    (yerel kopyalar kaynak değildir — depo eksik kopyalanmış olabilir)" >&2
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "  ✗ docker-compose.yml bulunamadı: $COMPOSE_FILE" >&2
    exit 1
fi

# Docker Compose servisindeki PostgreSQL'e bağlan.
PG_CMD=(
    docker compose -f "$COMPOSE_FILE"
    exec -T postgres
    psql -v ON_ERROR_STOP=1 -U otomaix -d otomaix
)

# Sıra SAYIYA göredir: `sort -n` satır başındaki numarayı okur (9 < 10), eşit
# numarada dosya adına düşer — testlerin keşfiyle (int, ad) aynı sıra. GNU'ya
# özel `find -printf` / `mapfile` bilinçli KULLANILMAZ: bu paket macOS'ta da
# koşar (bash 3.2 + BSD find).
MIGRATIONS=()
while IFS= read -r NAME; do
    [ -n "$NAME" ] || continue
    # Numarasız `.sql` dosyası sıralamayı belirsizleştirir → fail-closed.
    # (Aynı kural testlerin migration keşfinde de geçerli: tek gerçek, iki okuyucu.)
    if [[ ! "$NAME" =~ ^[0-9]+_ ]]; then
        echo "  ✗ Numarasız migration dosyası: $NAME — sıralama garanti edilemez." >&2
        exit 1
    fi
    MIGRATIONS+=("$NAME")
done < <(
    for FILE in "$MIGRATIONS_DIR"/*.sql; do
        [ -f "$FILE" ] || continue
        basename "$FILE"
    done | sort -n
)

if [ ${#MIGRATIONS[@]} -eq 0 ]; then
    echo "  ✗ Kanonik dizinde migration bulunamadı: $MIGRATIONS_DIR" >&2
    exit 1
fi

# social schema'yı oluştur (idempotent)
"${PG_CMD[@]}" -c "CREATE SCHEMA IF NOT EXISTS social;"

# pgvector extension'ını etkinleştir
"${PG_CMD[@]}" -c "CREATE EXTENSION IF NOT EXISTS vector;"

for MIGRATION in "${MIGRATIONS[@]}"; do
    echo "  → $MIGRATION"
    "${PG_CMD[@]}" -f /dev/stdin < "$MIGRATIONS_DIR/$MIGRATION"
done

echo "  ✓ Tüm migration'lar uygulandı (${#MIGRATIONS[@]} dosya)."
