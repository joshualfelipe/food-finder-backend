from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FOURSQUARE_API_KEY: str
    FOURSQUARE_BASE_URL: str
    FOURSQUARE_X_PLACES_API_VERSION: str

    GEOAPIFY_API_KEY: str
    GEOAPIFY_BASE_URL: str

    OPENAI_BASE_URL: str
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
