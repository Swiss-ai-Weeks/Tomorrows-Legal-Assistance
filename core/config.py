from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Build an absolute path to the .env file in the project root
# This makes the settings loading independent of the current working directory
ENV_PATH = Path(__file__).parent.parent / ".env"

print(f"Loading .env from: {ENV_PATH}")

class _Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore")

    # Apertus API Configuration
    APERTUS_API_KEY: str
    
    # Google API Configuration  
    GOOGLE_API_KEY: str


settings = _Settings()  # pyright: ignore[reportCallIssue]
