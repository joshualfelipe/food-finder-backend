from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEOAPIFY_API_KEY: str
    GEOAPIFY_BASE_URL: str

    OPENAI_BASE_URL: str
    OPENAI_API_KEY: str

    SUPABASE_URL: str
    SUPABASE_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
