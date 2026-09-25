import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "dev")
if ENV not in ("dev", "production"):
    raise RuntimeError(
        "ENV must be 'dev' or 'production' if set, e.g. `ENV=production "
        "python3 -m uvicorn main:app`"
    )

ENV_FILE = f".env.{ENV}"


class Settings(BaseSettings):
    GEOAPIFY_API_KEY: str
    GEOAPIFY_BASE_URL: str

    OPENAI_BASE_URL: str
    OPENAI_API_KEY: str

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=ENV_FILE)


settings = Settings()
