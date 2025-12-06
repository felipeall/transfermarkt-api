from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    RATE_LIMITING_ENABLE: bool = False
    RATE_LIMITING_FREQUENCY: str = "2/3seconds"

    # Anti-scraping configuration for Railway deployment
    SESSION_TIMEOUT: int = Field(default=3600, description="Session timeout in seconds (default: 1 hour)")
    MAX_SESSIONS: int = Field(default=50, description="Maximum concurrent sessions")
    MAX_CONCURRENT_REQUESTS: int = Field(default=10, description="Maximum concurrent requests per session")

    # Proxy configuration
    PROXY_HOST: Optional[str] = Field(default=None, description="Proxy host for residential proxies")
    PROXY_PORT: Optional[str] = Field(default=None, description="Proxy port")
    PROXY_USERNAME: Optional[str] = Field(default=None, description="Proxy authentication username")
    PROXY_PASSWORD: Optional[str] = Field(default=None, description="Proxy authentication password")

    # Anti-detection settings
    REQUEST_DELAY_MIN: float = Field(default=1.0, description="Minimum delay between requests (seconds)")
    REQUEST_DELAY_MAX: float = Field(default=3.0, description="Maximum delay between requests (seconds)")
    ENABLE_BEHAVIORAL_SIMULATION: bool = Field(  # noqa: E501
        default=False,
        description="Enable behavioral simulation (mouse movements, etc.)",
    )

    # Browser scraping configuration
    ENABLE_BROWSER_SCRAPING: bool = Field(default=True, description="Enable browser scraping fallback")
    BROWSER_TIMEOUT: int = Field(default=30000, description="Browser timeout in milliseconds")
    BROWSER_HEADLESS: bool = Field(default=True, description="Run browser in headless mode")

    # National team competition expected tournament sizes
    # Can be overridden via environment variables:
    # TOURNAMENT_SIZE_FIWC=48, TOURNAMENT_SIZE_EURO=24, etc.
    # Format: TOURNAMENT_SIZE_{COMPETITION_ID}=<number>
    TOURNAMENT_SIZE_FIWC: Optional[int] = Field(default=32, description="World Cup expected participants")
    TOURNAMENT_SIZE_EURO: Optional[int] = Field(default=24, description="UEFA Euro expected participants")
    TOURNAMENT_SIZE_COPA: Optional[int] = Field(default=12, description="Copa America expected participants")
    TOURNAMENT_SIZE_AFAC: Optional[int] = Field(default=24, description="AFC Asian Cup expected participants")
    TOURNAMENT_SIZE_GOCU: Optional[int] = Field(default=16, description="Gold Cup expected participants")
    TOURNAMENT_SIZE_AFCN: Optional[int] = Field(default=24, description="Africa Cup of Nations expected participants")

    @field_validator(
        "TOURNAMENT_SIZE_FIWC",
        "TOURNAMENT_SIZE_EURO",
        "TOURNAMENT_SIZE_COPA",
        "TOURNAMENT_SIZE_AFAC",
        "TOURNAMENT_SIZE_GOCU",
        "TOURNAMENT_SIZE_AFCN",
    )
    @classmethod
    def validate_tournament_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate tournament size is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("Tournament size must be a positive integer")
        return v

    def get_tournament_size(self, competition_id: str) -> Optional[int]:
        """
        Get expected tournament size for a competition ID.

        Args:
            competition_id: The competition ID (e.g., "FIWC", "EURO")

        Returns:
            Optional[int]: The expected tournament size, or None if not configured
        """
        size_map = {
            "FIWC": self.TOURNAMENT_SIZE_FIWC,
            "EURO": self.TOURNAMENT_SIZE_EURO,
            "COPA": self.TOURNAMENT_SIZE_COPA,
            "AFAC": self.TOURNAMENT_SIZE_AFAC,
            "GOCU": self.TOURNAMENT_SIZE_GOCU,
            "AFCN": self.TOURNAMENT_SIZE_AFCN,
        }
        return size_map.get(competition_id)


settings = Settings()
