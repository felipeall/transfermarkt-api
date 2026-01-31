from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    RATE_LIMITING_ENABLE: bool = False
    RATE_LIMITING_FREQUENCY: str = "2/3seconds"
    
    # ScrapingBee configuration for rotating IP addresses
    USE_SCRAPINGBEE: bool = False
    SCRAPINGBEE_API_KEY: str = ""
    SCRAPINGBEE_PREMIUM_PROXY: bool = True
    SCRAPINGBEE_COUNTRY_CODE: str = "de"  # German proxies for TransferMarkt


settings = Settings()
