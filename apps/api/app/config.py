from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Admin AI API"
    debug: bool = False
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://adminai:adminai@localhost:5432/adminai"
    redis_url: str = "redis://localhost:6379/0"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "admin-ai-documents"
    s3_region: str = "us-east-1"
    
    openai_api_key: str = ""

    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
