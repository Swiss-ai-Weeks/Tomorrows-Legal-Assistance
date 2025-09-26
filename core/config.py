from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Apertus Configuration
    APERTUS_API_KEY: str


settings = _Settings()  # pyright: ignore[reportCallIssue]
