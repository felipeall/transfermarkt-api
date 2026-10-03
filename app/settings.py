from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    RATE_LIMITING_ENABLE: bool = False
    RATE_LIMITING_FREQUENCY: str = "2/3seconds"

    TFMKT_BASE_URL: str = "https://tmapi.transfermarkt.technology"
    TFMKT_TIMEOUT_SECONDS: float = 15.0
    TFMKT_MAX_CONCURRENCY: int = 10
    CACHE_TTL_SECONDS: int = 600
    CACHE_REFERENCE_TTL_SECONDS: int = 86_400
    CACHE_MAX_ENTRIES: int = 2_000


settings = Settings()
