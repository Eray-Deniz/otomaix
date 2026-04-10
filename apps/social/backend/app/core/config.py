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


settings = Settings()
