from pydantic_settings import BaseSettings, SettingsConfigDict

# Alan ADINDAN sır teşhisi — elle bakılan liste DEĞİL (2026-09-12 güvenlik
# review'ı, S-8). Elle liste, yeni eklenen her anahtarda bakım borcu üretir ve
# unutulan tek satır sızıntının kendisidir.
_SIR_IPUCLARI = ("KEY", "SECRET", "TOKEN", "PASSWORD", "DSN", "DATABASE_URL")

_SIR_ISTISNALARI = frozenset({"R2_BUCKET_NAME", "R2_PUBLIC_URL"})
"""Adında ipucu geçse de sır OLMAYAN alanlar — açıkça sayılır, sessizce değil."""


def _sir_alani_mi(ad: str) -> bool:
    """Alan adı bir sır taşıyor mu? Tek kural, iki tüketici (temsil + testler)."""
    if ad in _SIR_ISTISNALARI:
        return False
    return any(ipucu in ad.upper() for ipucu in _SIR_IPUCLARI)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    FAL_KEY: str = ""
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_PUBLIC_URL: str = ""
    UPLOAD_POST_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    INTERNAL_API_KEY: str = ""  # n8n → backend servis kimlik doğrulaması
    OPENAI_API_KEY: str = ""    # Opsiyonel — RAG chunk embedding için
    ELEVENLABS_KEY: str = ""    # Opsiyonel — Kısa video TTS için
    HEYGEN_API_KEY: str = ""    # Opsiyonel — AI Avatar için
    APIFY_API_KEY: str = ""     # Opsiyonel — Instagram rakip analizi için
    PADDLE_API_KEY: str = ""    # Opsiyonel — Paddle ödeme entegrasyonu
    PADDLE_WEBHOOK_SECRET: str = ""  # Paddle webhook imza doğrulama
    APP_URL: str = "https://app.otomaix.com"
    POSTHOG_API_KEY: str = ""   # Opsiyonel — PostHog server-side analytics
    POSTHOG_HOST: str = "https://eu.posthog.com"
    SENTRY_DSN: str = ""        # Opsiyonel — Sentry error monitoring
    ENVIRONMENT: str = "production"  # development | production
    N8N_BASE_URL: str = "https://n8n.otomaix.com"  # n8n CRM webhook base URL
    # Yönetici olay webhook'unun kabul kontrolü. BOŞSA gönderim YAPILMAZ
    # (fail-closed): kimlik doğrulamasız bir webhook'a erişebilen herkes sahte
    # yönetici uyarısı üretebilirdi (checkpoint 14, F1).
    N8N_ADMIN_EVENT_SECRET: str = ""
    # CRM bildirim webhook'larının kabul kontrolü (2026-09-12 güvenlik review'ı,
    # S-1/critical). BOŞSA çağrı YAPILMAZ (fail-closed): üç CRM webhook'u
    # kimlik doğrulamasızdı ve ödeme akışı istek gövdesini SQL metnine gömüyordu.
    # Yönetici-olay sırrından AYRI tutulur — tek sır iki kanalı birden açardı.
    N8N_CRM_EVENT_SECRET: str = ""
    # Telegram içerik onay webhook'unun kabul kontrolü — aynı sınıf, aynı kapı
    # (2026-09-12 güvenlik review'ının sınıf kapısı bu ucu da kimliksiz buldu).
    N8N_TELEGRAM_APPROVAL_SECRET: str = ""
    # Phase 6 — Trend sistemi
    YOUTUBE_API_KEY: str = ""        # Opsiyonel — YouTube Data API v3 (Layer A)
    REDDIT_USER_AGENT: str = "otomaix-social/1.0 (+https://otomaix.com)"
    EVDS_API_KEY: str = ""           # Opsiyonel — TCMB EVDS (Layer A, finans)
    SERPER_API_KEY: str = ""         # Opsiyonel — Serper.dev Google Search (Layer B)
    # Phase 7 — Media model adapter registry keys
    IMAGE_MODEL: str = "flux-2-pro"  # app.services.media_adapters.IMAGE_ADAPTERS key
    VIDEO_MODEL: str = "kling-v3-pro"  # app.services.media_adapters.VIDEO_ADAPTERS key
    IMAGE_TO_VIDEO_MODEL: str = "kling-v25-turbo-pro"  # app.services.media_adapters.IMAGE_TO_VIDEO_ADAPTERS key
    SHORT_VIDEO_BACKGROUND_MODEL: str = "wan-i2v-flash"  # app.services.media_adapters.SHORT_VIDEO_BACKGROUND_ADAPTERS key
    # Phase 9 — Image-edit modality (ürün görseli + prompt → düzenlenmiş görsel)
    IMAGE_EDIT_MODEL: str = "nano-banana-2-edit"  # app.services.media_adapters.IMAGE_EDIT_ADAPTERS key


    def __repr__(self) -> str:
        """Sır taşıyan alanların DEĞERİ temsile GİRMEZ — yalnız maskesi.

        Pydantic'in varsayılan temsili bütün alanları basıyordu; ölçüldü
        (2026-09-12): tek bir `AttributeError` metni veritabanı parolasını,
        Supabase servis anahtarını, fal.ai/R2/Upload-Post/ElevenLabs
        anahtarlarını ve dâhilî API anahtarını birden yazdı. Aynı yol her yığın
        izinde ve hata izleme kaydında açıktı.

        Alan ADLARI korunur: maskeleme teşhisi öldürmemeli — hangi ayarın dolu,
        hangisinin boş olduğu görünür kalır.
        """
        parcalar = []
        for ad in type(self).model_fields:
            deger = getattr(self, ad, None)
            if _sir_alani_mi(ad):
                parcalar.append(f"{ad}={'<gizli:dolu>' if deger else '<gizli:boş>'}")
            else:
                parcalar.append(f"{ad}={deger!r}")
        return f"Settings({', '.join(parcalar)})"

    __str__ = __repr__


settings = Settings()
