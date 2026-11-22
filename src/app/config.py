"""Settings come from environment variables or a local .env file. Never hard-code secrets."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "offline" needs no key and is what CI uses; "anthropic" calls the Claude API.
    llm_provider: str = "offline"
    llm_model: str = "claude-haiku-5-5"
    anthropic_api_key: str | None = None
    max_output_tokens: int = 512

    docs_dir: Path = Path("data/sample_docs")
    top_k: int = 3


settings = Settings()
