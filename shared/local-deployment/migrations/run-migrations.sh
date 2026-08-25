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
# NOT: her migration dosya BAŞINA tek transaction'da koşar
# (`--single-transaction`) — `ON_ERROR_STOP=1` yalnız AKIŞI durdurur, YAPILANI
# geri almaz; bayraksız koşumda reddeden bir doğrulama bloğu kendinden önceki
# DDL'i commit edilmiş bırakır (ÖLÇÜLDÜ 2026-08-25). İKİ dosya sınıfı muaftır ve
# muafiyet aşağıda `SELF_MANAGED_TX` listesinde ADIYLA durur:
#   * `CREATE INDEX CONCURRENTLY` içerenler (011) — transaction bloğunda
#     KOŞAMAZ; atomik değildir, `IF NOT EXISTS` ile yeniden koşum tamamlar.
#   * Kendi `BEGIN/COMMIT`ini taşıyanlar (017) — zaten kendi kendine atomiktir.
#     Bunları sarmak GARANTİYİ ZAYIFLATIRDI: ÖLÇÜLDÜ — içteki `COMMIT` dıştaki
#     transaction'ı erken kapatıyor ve sonrasındaki her şey hatada bile kalıyor.

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
    # Keşif aşamasının işaretleri: kapı ilk veritabanı dokunuşundan ÖNCE koşar.
    case "$NAME" in
        SYMLINK_REJECTED:*)
            echo "  ✗ Symlink migration reddedildi: ${NAME#SYMLINK_REJECTED:}" >&2
            echo "    (baytlar kanonik dizinde durmalı — symlink hedefi bu ağacın dışında)" >&2
            exit 1 ;;
        NOT_A_REGULAR_FILE:*)
            echo "  ✗ Düz dosya olmayan migration girdisi: ${NAME#NOT_A_REGULAR_FILE:}" >&2
            exit 1 ;;
    esac
    # Numarasız `.sql` dosyası sıralamayı belirsizleştirir → fail-closed.
    # (Aynı kural testlerin migration keşfinde de geçerli: tek gerçek, iki okuyucu.)
    if [[ ! "$NAME" =~ ^[0-9]+_ ]]; then
        echo "  ✗ Numarasız migration dosyası: $NAME — sıralama garanti edilemez." >&2
        exit 1
    fi
    MIGRATIONS+=("$NAME")
done < <(
    for FILE in "$MIGRATIONS_DIR"/*.sql; do
        # Glob eşleşmesi YOKSA desen kendisi gelir — o tek meşru atlama.
        [ -e "$FILE" ] || [ -L "$FILE" ] || continue
        # Symlink REDDEDİLİR (SESSİZCE ATLANMAZ). `-f` symlink'i İZLER: kanonik
        # dizindeki numaralı bir symlink, baytları bu ağacın DIŞINDA duran (ve
        # orada değişebilen) SQL'i canlıya uygulatabilirdi. SARKIK symlink ise
        # `-f`ye takılıp sessizce atlanırdı — "dosya var ama uygulanmadı" en
        # kötüsü, çünkü eksik migration hiç haber vermez.
        if [ -L "$FILE" ]; then
            echo "SYMLINK_REJECTED:$(basename "$FILE")"
            continue
        fi
        [ -f "$FILE" ] || { echo "NOT_A_REGULAR_FILE:$(basename "$FILE")"; continue; }
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

# Her migration KENDİ transaction'ında koşar (`--single-transaction`).
#
# Neden: `ON_ERROR_STOP=1` yalnız AKIŞI durdurur, YAPILANI geri almaz. Bir
# migration'ın sonundaki doğrulama bloğu reddettiğinde, o dosyanın daha önce
# uyguladığı DDL commit edilmiş kalırdı — yani başarısız bir dağıtım yarım
# değişmiş bir şema bırakırdı. ÖLÇÜLDÜ (2026-08-25): transaction'sız koşumda
# doğrulama hatasından önceki tablo AYAKTA kalıyor, `--single-transaction` ile
# geri alınıyor.
#
# MUAFİYET ELLE ve AÇIKÇA tutulur — dosya içeriğine bakıp "bu transaction'a
# girer mi" diye karar veren bir metin taraması semantik bir olumsuzu tahmin
# etmeye çalışırdı. Liste ile gerçeklik arasındaki uyum
# `test_migration_032_rollback.py::test_single_transaction_exemption_is_exact`
# ile İKİ YÖNLÜ bağlanır: muaf olan dosyanın iki gerekçeden BİRİ olmalı, muaf
# olmayan hiçbirinde İKİSİ DE olmamalı.
SELF_MANAGED_TX=("011_performance_indexes.sql" "017_trend_cache_unique.sql")

for MIGRATION in "${MIGRATIONS[@]}"; do
    EXEMPT=0
    for NAME in "${SELF_MANAGED_TX[@]}"; do
        [ "$MIGRATION" = "$NAME" ] && EXEMPT=1
    done
    if [ "$EXEMPT" -eq 1 ]; then
        echo "  → $MIGRATION"
        echo "     (dış transaction YOK — dosya kendi transaction anlambilimini taşır)"
        "${PG_CMD[@]}" -f /dev/stdin < "$MIGRATIONS_DIR/$MIGRATION"
    else
        echo "  → $MIGRATION"
        "${PG_CMD[@]}" --single-transaction -f /dev/stdin < "$MIGRATIONS_DIR/$MIGRATION"
    fi
done

echo "  ✓ Tüm migration'lar uygulandı (${#MIGRATIONS[@]} dosya)."
