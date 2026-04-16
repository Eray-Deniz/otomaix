"""
Otomaix Social — Locust Load Test
==================================
Hedef: 50 eş zamanlı kullanıcı, ortalama yanıt süresi < 500ms

Kurulum:
    pip install locust

Kullanım (production):
    export OTOMAIX_JWT="<supabase_jwt_token>"
    locust -f locustfile.py --host=https://api.otomaix.com

Kullanım (local):
    export OTOMAIX_JWT="<supabase_jwt_token>"
    locust -f locustfile.py --host=http://localhost:8000

Headless (CI):
    locust -f locustfile.py --host=https://api.otomaix.com \
           --users=50 --spawn-rate=5 --run-time=60s --headless \
           --csv=results/load_test

NOT: OTOMAIX_JWT yoksa /health-only moduna geçer (auth gerektirmeyen endpoint'ler).
NOT: generate_content görevi gerçek fal.ai çağrısı yapar — production'da dikkatli kullan.
     Sahte üretim için MOCK_GENERATE=1 ortam değişkeni set et.
"""

import os
import random

from locust import HttpUser, between, task

# ── Konfigürasyon ─────────────────────────────────────────────────────────────

JWT_TOKEN = os.getenv("OTOMAIX_JWT", "")
MOCK_GENERATE = os.getenv("MOCK_GENERATE", "0") == "1"

AUTH_HEADERS = {"Authorization": f"Bearer {JWT_TOKEN}"} if JWT_TOKEN else {}

SAMPLE_PROMPTS = [
    "Yazlık koleksiyon tanıtımı için Instagram postu",
    "Müşteri memnuniyeti hakkında ilham verici bir paylaşım",
    "Yeni ürün lansmanı duyurusu",
    "Haftanın ipuçları serisi için içerik",
    "Sezon indirimi kampanyası görseli",
]

CONTENT_TYPES = ["image", "carousel"]
CONTENT_CATEGORIES = ["product", "educational", "promotional", "lifestyle"]


# ── Health-only kullanıcı (JWT olmadan) ─────────────────────────────────────

class HealthOnlyUser(HttpUser):
    """JWT bulunamadığında yalnızca herkese açık endpoint'leri test eder."""

    wait_time = between(1, 3)

    @task
    def health_check(self):
        with self.client.get("/health", catch_response=True) as resp:
            if resp.status_code == 200:
                data = resp.json()
                if data.get("data", {}).get("status") != "ok":
                    resp.failure(f"Health degraded: {data}")
            else:
                resp.failure(f"HTTP {resp.status_code}")

    @task
    def billing_plans(self):
        self.client.get("/billing/plans")


# ── Authenticated kullanıcı ────────────────────────────────────────────────────

class OtomaixUser(HttpUser):
    """
    Kimliği doğrulanmış bir kullanıcının tipik oturumunu simüle eder.
    Ağırlıklar gerçek kullanım oranlarına yakındır.
    """

    wait_time = between(1, 3)
    brand_id: str | None = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_start(self):
        """Oturum başlangıcında markayı yükle."""
        with self.client.get("/auth/init", headers=AUTH_HEADERS, catch_response=True) as resp:
            if resp.status_code == 200:
                data = resp.json()
                brands = data.get("data", {}).get("brands", [])
                if brands:
                    self.brand_id = brands[0]["id"]
            elif resp.status_code == 401:
                resp.failure("JWT geçersiz veya süresi dolmuş")
            else:
                resp.failure(f"auth/init HTTP {resp.status_code}")

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task(3)
    def view_dashboard(self):
        """
        Dashboard yükleme: marka listesi + takvim önizlemesi.
        En sık çalışan senaryo (ağırlık=3).
        """
        if not self.brand_id:
            return

        from datetime import date, timedelta
        today = date.today()
        start = today.isoformat()
        end = (today + timedelta(days=30)).isoformat()

        self.client.get("/brands", headers=AUTH_HEADERS, name="/brands")
        self.client.get(
            f"/calendar/posts?brand_id={self.brand_id}&start={start}&end={end}",
            headers=AUTH_HEADERS,
            name="/calendar/posts",
        )

    @task(2)
    def browse_content_library(self):
        """
        İçerik kütüphanesi gezinme — ilk 2 sayfa.
        Ağırlık=2 (dashboard'dan sonra en sık).
        """
        if not self.brand_id:
            return

        page = random.choice([1, 2])
        self.client.get(
            f"/posts?brand_id={self.brand_id}&page={page}&limit=20",
            headers=AUTH_HEADERS,
            name="/posts (list)",
        )

    @task(2)
    def view_trends(self):
        """Trend sayfası — cache'li (3600s TTL), hızlı olmalı."""
        if not self.brand_id:
            return
        self.client.get(
            f"/trends?brand_id={self.brand_id}",
            headers=AUTH_HEADERS,
            name="/trends",
        )

    @task(1)
    def trigger_personal_trends(self):
        """Layer B kişisel trend araması — Serper.dev + Claude Haiku."""
        if not self.brand_id:
            return
        with self.client.post(
            f"/trends/personal?brand_id={self.brand_id}",
            json={},
            headers=AUTH_HEADERS,
            name="/trends/personal (Layer B)",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 402):
                response.success()

    @task(1)
    def view_calendar_holidays(self):
        """Resmi tatiller — yıllık cache (86400s TTL)."""
        from datetime import date
        year = date.today().year
        self.client.get(
            f"/calendar/holidays?year={year}",
            headers=AUTH_HEADERS,
            name="/calendar/holidays",
        )

    @task(1)
    def view_competitors(self):
        """Rakip listesi."""
        if not self.brand_id:
            return
        self.client.get(
            f"/competitors?brand_id={self.brand_id}",
            headers=AUTH_HEADERS,
            name="/competitors",
        )

    @task(1)
    def generate_content(self):
        """
        İçerik üretimi — fal.ai çağrısı başlatır (async, POST hemen döner).
        MOCK_GENERATE=1 ise atlanır.
        Ağırlık=1 (en az sıklık — rate limit: 20/saat).
        """
        if not self.brand_id or MOCK_GENERATE:
            return

        payload = {
            "brand_id": self.brand_id,
            "content_type": random.choice(CONTENT_TYPES),
            "content_category": random.choice(CONTENT_CATEGORIES),
            "prompt": random.choice(SAMPLE_PROMPTS),
            "platforms": ["instagram"],
        }

        with self.client.post(
            "/posts/generate",
            json=payload,
            headers=AUTH_HEADERS,
            catch_response=True,
            name="/posts/generate",
        ) as resp:
            if resp.status_code == 429:
                # Rate limit beklenen bir durum — failure sayılmasın
                resp.success()
            elif resp.status_code not in (200, 201):
                resp.failure(f"HTTP {resp.status_code}: {resp.text[:200]}")

    @task(1)
    def health_check(self):
        """Health endpoint — DB + Redis durumu."""
        with self.client.get("/health", catch_response=True) as resp:
            if resp.status_code == 200:
                data = resp.json()
                if data.get("data", {}).get("status") == "degraded":
                    resp.failure(f"Service degraded: {data}")
            else:
                resp.failure(f"HTTP {resp.status_code}")


# ── Kullanıcı sınıfı seçimi ────────────────────────────────────────────────────

# JWT yoksa sadece health endpoint'lerini test et
if not JWT_TOKEN:
    print(
        "\n⚠  OTOMAIX_JWT bulunamadı — yalnızca herkese açık endpoint'ler test edilecek.\n"
        "   export OTOMAIX_JWT='<token>' ile tam test için token ekleyin.\n"
    )
    # OtomaixUser'ı devre dışı bırak (weight=0 mümkün olmadığı için sınıfı kaldır)
    del OtomaixUser
