#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "=================================================="
echo "  Otomaix Social — Yerel Kurulum Sihirbazı"
echo "=================================================="
echo ""

# ── 1. Docker kontrolü ───────────────────────────────────────────────────────
echo "🔍 Docker kontrol ediliyor..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker bulunamadı.${NC}"
    echo "  Lütfen Docker Desktop'ı kurun: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose (v2) bulunamadı.${NC}"
    echo "  Docker Desktop güncel değil olabilir. Lütfen güncelleyin."
    exit 1
fi

echo -e "${GREEN}✓ Docker $(docker --version | cut -d' ' -f3 | tr -d ',') hazır${NC}"

# ── 2. .env hazırlama ────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 .env dosyası oluşturuluyor..."
    cp .env.example .env
    echo -e "${YELLOW}⚠  .env dosyasını açıp gerekli API anahtarlarını doldurun:${NC}"
    echo "   - SUPABASE_URL ve SUPABASE_SERVICE_KEY"
    echo "   - FAL_KEY (görsel/video üretimi)"
    echo "   - ANTHROPIC_API_KEY (AI içerik)"
    echo "   - R2_* (medya depolama)"
    echo "   - POSTGRES_PASSWORD (güçlü bir şifre seçin)"
    echo "   - N8N_ENCRYPTION_KEY (32+ karakter rastgele)"
    echo ""
    echo "Düzenlemeyi tamamladıktan sonra bu scripti tekrar çalıştırın."
    echo ""
    echo "  nano .env   veya   code .env"
    echo ""
    exit 0
else
    echo -e "${GREEN}✓ .env dosyası mevcut${NC}"
fi

# ── 3. Gerekli env değişken kontrolü ────────────────────────────────────────
echo ""
echo "🔑 Zorunlu değişkenler kontrol ediliyor..."

source .env 2>/dev/null || true

REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY"
    "FAL_KEY"
    "ANTHROPIC_API_KEY"
    "INTERNAL_API_KEY"
    "N8N_ENCRYPTION_KEY"
    "NEXT_PUBLIC_SUPABASE_URL"
    "NEXT_PUBLIC_SUPABASE_ANON_KEY"
)

MISSING=()
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        MISSING+=("$VAR")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}✗ Eksik değişkenler (.env içinde boş bırakılmış):${NC}"
    for VAR in "${MISSING[@]}"; do
        echo "   - $VAR"
    done
    echo ""
    echo "Lütfen .env dosyasını düzenleyip tekrar çalıştırın."
    exit 1
fi

echo -e "${GREEN}✓ Tüm zorunlu değişkenler dolu${NC}"

# ── 4. Image'ları çek ───────────────────────────────────────────────────────
echo ""
echo "📦 Docker image'ları indiriliyor (ilk seferde birkaç dakika sürebilir)..."
docker compose pull

# ── 5. Servisleri başlat ─────────────────────────────────────────────────────
echo ""
echo "🚀 Servisler başlatılıyor..."
docker compose up -d postgres redis

echo ""
echo "⏳ PostgreSQL hazır olana kadar bekleniyor..."
until docker compose exec -T postgres pg_isready -U otomaix -d otomaix &>/dev/null; do
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL hazır${NC}"

# ── 6. Migration'ları çalıştır ───────────────────────────────────────────────
echo ""
echo "🗄  Veritabanı migration'ları çalıştırılıyor..."
bash migrations/run-migrations.sh
echo -e "${GREEN}✓ Migration'lar tamamlandı${NC}"

# ── 7. Tüm servisleri başlat ─────────────────────────────────────────────────
echo ""
echo "🚀 Tüm servisler başlatılıyor..."
docker compose up -d

echo ""
echo "⏳ Backend hazır olana kadar bekleniyor..."
RETRIES=0
until curl -sf http://localhost:8000/health &>/dev/null || [ $RETRIES -ge 20 ]; do
    sleep 3
    RETRIES=$((RETRIES + 1))
done

if curl -sf http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✓ Backend hazır${NC}"
else
    echo -e "${YELLOW}⚠  Backend henüz hazır değil, logları kontrol edin: docker compose logs backend${NC}"
fi

# ── 8. Tamamlandı ────────────────────────────────────────────────────────────
echo ""
echo "=================================================="
echo -e "${GREEN}  ✅ Kurulum tamamlandı!${NC}"
echo "=================================================="
echo ""
echo "  Frontend : http://localhost:3000"
echo "  Backend  : http://localhost:8000/docs"
echo "  n8n      : http://localhost:5678"
echo ""
echo "  Logları görmek için:"
echo "    docker compose logs -f"
echo ""
echo "  Durdurmak için:"
echo "    docker compose down"
echo ""
