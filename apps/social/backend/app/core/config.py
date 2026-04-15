from pydantic_settings import BaseSettings, SettingsConfigDict


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
    AZURE_TTS_KEY: str = ""     # Opsiyonel — Faceless video TTS için
    AZURE_TTS_REGION: str = "westeurope"  # Azure TTS bölgesi
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
    # Phase 6 — Trend sistemi
    YOUTUBE_API_KEY: str = ""        # Opsiyonel — YouTube Data API v3 (Layer A)
    REDDIT_USER_AGENT: str = "otomaix-social/1.0 (+https://otomaix.com)"
    PRODUCT_HUNT_TOKEN: str = ""     # Opsiyonel — Product Hunt GraphQL bearer (Layer A)
    EVDS_API_KEY: str = ""           # Opsiyonel — TCMB EVDS (Layer A, finans)
    SERPER_API_KEY: str = ""         # Opsiyonel — Serper.dev Google Search (Layer B)
    SPOTIFY_CLIENT_ID: str = ""      # Opsiyonel — Spotify Web API (Layer A)
    SPOTIFY_CLIENT_SECRET: str = ""


settings = Settings()
