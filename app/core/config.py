from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central app configuration, loaded from environment variables (or a .env file).
    Never hardcode secrets/connection strings directly in code — this is the pattern
    interviewers expect to see instead of the flat hardcoded-config style.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Postgres
    database_url: str = "postgresql://postgres:postgres@localhost:5432/pricetracker"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day


settings = Settings()
