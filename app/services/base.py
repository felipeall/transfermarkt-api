import asyncio
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from lxml import etree
from requests import Response, Session, TooManyRedirects

try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None  # type: ignore

from app.settings import settings
from app.utils.utils import trim
from app.utils.xpath import Pagination


class SmartSessionManager:
    """
    Advanced session manager with User-Agent rotation, proxy support, and anti-detection measures.

    Features:
    - User-Agent rotation from curated list of real browser fingerprints
    - Session persistence with configurable timeouts
    - Proxy rotation support (Railway environment variables)
    - Request fingerprinting avoidance through header randomization
    """

    def __init__(self):
        """Initialize the SmartSessionManager with user agents, proxies, and session settings."""
        self.sessions: Dict[str, Dict] = {}
        self.user_agents = self._load_user_agents()
        self.proxies = self._load_proxies()
        self.session_timeout = settings.SESSION_TIMEOUT
        self.max_sessions = settings.MAX_SESSIONS

    def _load_user_agents(self) -> List[str]:
        """Load curated list of real browser User-Agents."""
        return [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",  # noqa: E501
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",  # noqa: E501
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa: E501
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",  # noqa: E501
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",  # noqa: E501
            # Firefox Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
            # Firefox macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            # Safari macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",  # noqa: E501
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",  # noqa: E501
            # Edge Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",  # noqa: E501
            # Chrome Linux (for Railway compatibility)
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        ]

    def _load_proxies(self) -> List[Dict[str, str]]:
        """Load proxy configuration from Railway environment variables."""
        proxies = []

        # Support for Bright Data / Oxylabs residential proxies
        if all([settings.PROXY_HOST, settings.PROXY_PORT, settings.PROXY_USERNAME, settings.PROXY_PASSWORD]):
            proxy_url = f"http://{settings.PROXY_USERNAME}:{settings.PROXY_PASSWORD}@{settings.PROXY_HOST}:{settings.PROXY_PORT}"
            proxies.append(
                {
                    "http": proxy_url,
                    "https": proxy_url,
                },
            )

        # Support for multiple proxy endpoints via environment variables
        for i in range(1, 11):  # Support up to 10 proxies
            proxy_url = os.getenv(f"PROXY_URL_{i}")
            if proxy_url:
                proxies.append(
                    {
                        "http": proxy_url,
                        "https": proxy_url,
                    },
                )

        return proxies

    def get_session(self, session_id: str = None) -> Session:
        """
        Get or create a session with anti-detection measures.

        Args:
            session_id: Optional session identifier for persistence

        Returns:
            requests.Session: Configured session with anti-bot headers
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        # Clean up expired sessions
        self._cleanup_expired_sessions()

        # Return existing session if available
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            if not self._is_session_expired(session_data):
                return session_data["session"]

        # Create new session
        session = self._create_session()
        self.sessions[session_id] = {
            "session": session,
            "created_at": self._get_timestamp(),
            "user_agent": session.headers.get("User-Agent"),
            "proxy": self._get_random_proxy() if self.proxies else None,
        }

        # Record session creation
        _monitor.record_session_created()

        # Enforce max sessions limit
        if len(self.sessions) > self.max_sessions:
            self._cleanup_oldest_session()

        return session

    def _create_session(self) -> Session:
        """Create a new session with anti-detection headers."""
        session = requests.Session()

        # Set random User-Agent
        user_agent = random.choice(self.user_agents)
        session.headers.update(self._generate_headers(user_agent))

        # Set proxy if available
        if self.proxies:
            proxy = self._get_random_proxy()
            session.proxies.update(proxy)

        return session

    def _generate_headers(self, user_agent: str) -> Dict[str, str]:
        """Generate browser-like headers with randomization."""
        # Randomize Accept-Language for geo diversity
        accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "en-US,en;q=0.9,de;q=0.8",
            "en-US,en;q=0.9,fr;q=0.8",
            "en-US,en;q=0.9,nl;q=0.8",
        ]

        # Randomize Sec-Fetch headers slightly
        sec_fetch_values = [
            ("navigate", "navigate", "same-origin", "?1"),
            ("document", "navigate", "same-origin", "?1"),
            ("navigate", "navigate", "none", "?1"),
        ]
        sec_fetch_dest, sec_fetch_mode, sec_fetch_site, sec_fetch_user = random.choice(sec_fetch_values)

        headers = {
            "User-Agent": user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            ),  # noqa: E501
            "Accept-Language": random.choice(accept_languages),
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.transfermarkt.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": sec_fetch_dest,
            "Sec-Fetch-Mode": sec_fetch_mode,
            "Sec-Fetch-Site": sec_fetch_site,
            "Sec-Fetch-User": sec_fetch_user,
            "Cache-Control": "max-age=0",
            "DNT": "1",  # Do Not Track header
        }

        # Add Chrome-specific headers if User-Agent contains Chrome
        if "Chrome" in user_agent:
            headers["Sec-Ch-Ua"] = '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"'
            headers["Sec-Ch-Ua-Mobile"] = "?0"
            headers["Sec-Ch-Ua-Platform"] = '"Windows"' if "Windows" in user_agent else '"macOS"'

        return headers

    def _get_random_proxy(self) -> Dict[str, str]:
        """Get a random proxy from the proxy pool."""
        return random.choice(self.proxies) if self.proxies else {}

    def _get_timestamp(self) -> float:
        """Get current timestamp for session management."""
        import time

        return time.time()

    def _is_session_expired(self, session_data: Dict) -> bool:
        """Check if a session has expired."""
        import time

        return time.time() - session_data["created_at"] > self.session_timeout

    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        import time

        current_time = time.time()
        expired_sessions = [
            session_id
            for session_id, data in self.sessions.items()
            if current_time - data["created_at"] > self.session_timeout
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]

    def _cleanup_oldest_session(self):
        """Remove the oldest session when max sessions limit is reached."""
        if not self.sessions:
            return

        oldest_session = min(self.sessions.items(), key=lambda x: x[1]["created_at"])
        del self.sessions[oldest_session[0]]

    def get_session_stats(self) -> Dict:
        """Get statistics about current sessions."""

        active_sessions = len([s for s in self.sessions.values() if not self._is_session_expired(s)])
        total_sessions = len(self.sessions)
        proxies_available = len(self.proxies)

        return {
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "expired_sessions": total_sessions - active_sessions,
            "proxies_available": proxies_available,
            "user_agents_available": len(self.user_agents),
            "session_timeout_seconds": self.session_timeout,
        }


# Global session manager instance
_session_manager = SmartSessionManager()


class AntiScrapingMonitor:
    """
    Monitor for tracking anti-scraping performance and success rates.

    Tracks request success/failure rates, block detection, and session performance.
    """

    def __init__(self):
        """Initialize the AntiScrapingMonitor with default metrics."""
        self.requests_total = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.blocks_detected = 0
        self.retries_performed = 0
        self.sessions_created = 0
        self.avg_response_time = 0.0
        self.browser_requests = 0
        self.browser_successes = 0
        self.last_reset = self._get_timestamp()

    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time

        return time.time()

    def record_request(self, success: bool, response_time: float = 0.0, was_blocked: bool = False):
        """Record a request result."""
        self.requests_total += 1
        if success:
            self.requests_successful += 1
        else:
            self.requests_failed += 1

        if was_blocked:
            self.blocks_detected += 1

        if response_time > 0:
            # Calculate running average
            self.avg_response_time = (
                self.avg_response_time * (self.requests_total - 1) + response_time
            ) / self.requests_total  # noqa: E501

    def record_retry(self):
        """Record that a retry was performed."""
        self.retries_performed += 1

    def record_session_created(self):
        """Record that a new session was created."""
        self.sessions_created += 1

    def record_browser_request(self, success: bool = False):
        """Record a browser scraping attempt."""
        self.browser_requests += 1
        if success:
            self.browser_successes += 1

    def get_stats(self) -> Dict:
        """Get comprehensive monitoring statistics."""
        import time

        uptime = time.time() - self.last_reset

        success_rate = (self.requests_successful / self.requests_total * 100) if self.requests_total > 0 else 0
        block_rate = (self.blocks_detected / self.requests_total * 100) if self.requests_total > 0 else 0

        browser_success_rate = (
            (self.browser_successes / self.browser_requests * 100) if self.browser_requests > 0 else 0
        )  # noqa: E501

        return {
            "uptime_seconds": uptime,
            "requests_total": self.requests_total,
            "requests_successful": self.requests_successful,
            "requests_failed": self.requests_failed,
            "success_rate_percent": round(success_rate, 2),
            "blocks_detected": self.blocks_detected,
            "block_rate_percent": round(block_rate, 2),
            "retries_performed": self.retries_performed,
            "sessions_created": self.sessions_created,
            "avg_response_time_seconds": round(self.avg_response_time, 3),
            "browser_requests": self.browser_requests,
            "browser_successes": self.browser_successes,
            "browser_success_rate_percent": round(browser_success_rate, 2),
            "session_manager_stats": _session_manager.get_session_stats(),
            "retry_manager_stats": _retry_manager.get_retry_stats(),
        }

    def reset_stats(self):
        """Reset all statistics (useful for testing)."""
        self.requests_total = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.blocks_detected = 0
        self.retries_performed = 0
        self.sessions_created = 0
        self.avg_response_time = 0.0
        self.browser_requests = 0
        self.browser_successes = 0
        self.last_reset = self._get_timestamp()


# Global monitoring instance
_monitor = AntiScrapingMonitor()


class PlaywrightBrowserScraper:
    """
    Advanced browser scraper using Playwright for JavaScript-heavy anti-bot bypass.

    Features:
    - Real browser fingerprinting
    - JavaScript execution
    - Behavioral simulation
    - Cloudflare bypass capabilities
    - Automatic fallback handling
    """

    def __init__(self):
        """Initialize the PlaywrightBrowserScraper with user agents and viewport sizes."""
        self.user_agents = _session_manager.user_agents
        self.viewport_sizes = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
        ]
        self.timeout = settings.BROWSER_TIMEOUT
        self.headless = settings.BROWSER_HEADLESS

    async def scrape_with_browser(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Scrape a webpage using Playwright browser simulation.

        Args:
            url: URL to scrape
            wait_for_selector: Optional CSS selector to wait for before returning content

        Returns:
            HTML content as string

        Raises:
            ImportError: If playwright is not installed.
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright is not installed. Install it with: pip install playwright")

        async with async_playwright() as p:
            # Launch browser with anti-detection measures
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            )

            try:
                # Create context with realistic settings
                context = await browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport=random.choice(self.viewport_sizes),
                    locale="en-US",
                    timezone_id="Europe/Copenhagen",
                    geolocation={"latitude": 55.6761, "longitude": 12.5683},  # Copenhagen coordinates
                    permissions=["geolocation"],
                    # Reduce fingerprinting
                    device_scale_factor=1,
                    is_mobile=False,
                    has_touch=False,
                )

                # Add realistic browser properties
                await self._add_stealth_measures(context)

                page = await context.new_page()

                # Set additional headers to mimic real browser
                await page.set_extra_http_headers(
                    {
                        "Accept": (
                            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
                        ),  # noqa: E501
                        "Accept-Language": "en-US,en;q=0.9,da;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                    },
                )

                # Navigate with realistic timing
                await page.goto(url, wait_until="domcontentloaded")

                # Wait for potential anti-bot checks (reduced delay for speed)
                # If behavioral simulation is disabled, use minimal delay
                if settings.ENABLE_BEHAVIORAL_SIMULATION:
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    await self._simulate_human_behavior(page)
                else:
                    # Minimal delay when behavioral simulation is off
                    await asyncio.sleep(random.uniform(0.2, 0.5))

                # Wait for specific selector if provided
                if wait_for_selector:
                    try:
                        await page.wait_for_selector(wait_for_selector, timeout=self.timeout)
                    except Exception:
                        pass  # Continue even if selector not found

                # Wait for network to be idle (with timeout to avoid hanging)
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)  # 5 second timeout
                except Exception:
                    pass  # Continue even if networkidle times out

                # Get final HTML content
                content = await page.content()

                return content

            finally:
                await browser.close()

    async def _add_stealth_measures(self, context):
        """Add stealth measures to reduce browser fingerprinting."""
        # Override navigator properties
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Override plugins (make it look like a real browser)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer'
                    },
                    { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' }
                ],
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'da'],
            });

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)  # noqa: E501, Q000

    async def _simulate_human_behavior(self, page):
        """Simulate human-like browsing behavior (optimized for speed)."""
        # Minimal scrolling (reduced for speed)
        scroll_amount = random.randint(300, 800)
        await page.evaluate(f"window.scrollTo(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.2, 0.5))

        # Minimal mouse movements (reduced count and delay)
        viewport = await page.viewport_size()
        for _ in range(random.randint(1, 3)):  # Reduced from 3-8 to 1-3
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.05, 0.2))  # Reduced delay

        # Quick scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(random.uniform(0.3, 0.6))  # Reduced from 1-2 seconds

    async def scrape_with_fallback(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Scrape with browser as primary method, HTTP fallback.

        Args:
            url: URL to scrape
            wait_for_selector: Optional CSS selector to wait for

        Returns:
            HTML content as string
        """
        try:
            # Try browser scraping first
            return await self.scrape_with_browser(url, wait_for_selector)
        except Exception as e:
            print(f"Browser scraping failed for {url}: {e}")
            # Fallback to HTTP request
            response = _retry_manager.execute_with_retry(
                lambda: requests.get(url, headers=_session_manager.get_session().headers),
            )
            return response.text


# Global browser scraper instance (only if playwright is available)
_browser_scraper: Optional[PlaywrightBrowserScraper] = PlaywrightBrowserScraper() if PLAYWRIGHT_AVAILABLE else None


class RetryManager:
    """
    Intelligent retry manager with exponential backoff and anti-detection delays.

    Features:
    - Exponential backoff with jitter
    - Smart delay calculation based on response codes
    - Session rotation on persistent failures
    - Railway-optimized for resource constraints
    """

    def __init__(self):
        """Initialize the RetryManager with retry configuration from settings."""
        self.max_attempts = 3
        self.base_delay = settings.REQUEST_DELAY_MIN
        self.max_delay = settings.REQUEST_DELAY_MAX
        self.exponential_base = 2
        self.jitter_factor = 0.1

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with intelligent retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Any: Result of the function execution

        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                # Add random delay between requests (anti-detection)
                if attempt > 0:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
                    # Record retry
                    _monitor.record_retry()

                result = func(*args, **kwargs)
                return result

            except (requests.exceptions.RequestException, HTTPException) as e:
                last_exception = e

                # Don't retry on client errors (4xx) except rate limits
                if hasattr(e, "status_code") and 400 <= e.status_code < 500:
                    if e.status_code in [429, 503]:  # Rate limit or service unavailable
                        continue  # Retry these
                    else:
                        raise  # Don't retry other 4xx errors

                # For other errors, continue to retry logic
                if attempt == self.max_attempts - 1:
                    raise last_exception

                # Log retry attempt
                print(f"Request failed (attempt {attempt + 1}/{self.max_attempts}): {e}")

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay with exponential backoff and jitter.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            float: Delay in seconds
        """
        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        exponential_delay = self.base_delay * (self.exponential_base**attempt)

        # Add jitter to avoid detection patterns
        jitter = random.uniform(-self.jitter_factor, self.jitter_factor) * exponential_delay
        delay = exponential_delay + jitter

        # Cap at max_delay
        return min(delay, self.max_delay)

    async def execute_with_retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Async version of execute_with_retry for async functions.

        Args:
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Any: Result of the function execution
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                if attempt > 0:
                    delay = self._calculate_delay(attempt)
                    await asyncio.sleep(delay)

                result = await func(*args, **kwargs)
                return result

            except (requests.exceptions.RequestException, HTTPException) as e:
                last_exception = e

                if hasattr(e, "status_code") and 400 <= e.status_code < 500:
                    if e.status_code in [429, 503]:
                        continue
                    else:
                        raise

                if attempt == self.max_attempts - 1:
                    raise last_exception

                print(f"Async request failed (attempt {attempt + 1}/{self.max_attempts}): {e}")

    def get_retry_stats(self) -> Dict:
        """
        Get retry manager statistics and configuration.

        Returns:
            Dict: Retry configuration and performance metrics.
        """
        return {
            "max_attempts": self.max_attempts,
            "base_delay_seconds": self.base_delay,
            "max_delay_seconds": self.max_delay,
            "exponential_base": self.exponential_base,
            "jitter_factor": self.jitter_factor,
            "delay_range": f"{self.base_delay:.1f}-{self.max_delay:.1f}s",
        }


# Global retry manager instance
_retry_manager = RetryManager()


@dataclass
class TransfermarktBase:
    """
    Base class for making HTTP requests to Transfermarkt and extracting data from the web pages.

    Uses SmartSessionManager for advanced anti-detection measures including:
    - User-Agent rotation
    - Proxy support
    - Session persistence
    - Request fingerprinting avoidance

    Args:
        URL (str): The URL for the web page to be fetched.
        session_id (str, optional): Session identifier for persistence across requests.
    Attributes:
        page (ElementTree): The parsed web page content.
        response (dict): A dictionary to store the response data.
        session (Session): Smart session with anti-detection measures.
    """

    URL: str
    session_id: Optional[str] = field(default=None)
    page: ElementTree = field(default_factory=lambda: None, init=False)
    response: dict = field(default_factory=lambda: {}, init=False)
    session: Session = field(default_factory=lambda: None, init=False)

    def __post_init__(self):
        """Initialize the session using SmartSessionManager for anti-bot protection."""
        if self.session is None:
            self.session = _session_manager.get_session(self.session_id)

    def make_request_with_browser_fallback(self, url: Optional[str] = None, use_browser: bool = None) -> Response:
        """
        Make request with browser fallback for advanced anti-bot bypass.

        Args:
            url: URL to request
            use_browser: Whether to try browser scraping on HTTP failure

        Returns:
            Response object (with .text containing HTML)
        """
        url = self.URL if not url else url

        # Use settings as default if use_browser not specified
        if use_browser is None:
            use_browser = settings.ENABLE_BROWSER_SCRAPING

        # Try HTTP request first
        try:
            return self.make_request(url)
        except Exception as http_error:
            if not use_browser:
                raise http_error

            print(f"HTTP request failed, trying browser fallback for {url}")

            # Create a mock Response object with browser content
            if not PLAYWRIGHT_AVAILABLE or _browser_scraper is None:
                raise http_error

            try:
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                html_content = loop.run_until_complete(_browser_scraper.scrape_with_fallback(url))

                # Validate browser content
                if not html_content or len(html_content) < 100:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Browser scraping returned empty or invalid content for {url}",
                    )

                # Track successful browser request
                _monitor.record_browser_request(success=True)

                # Create mock response
                mock_response = Response()
                mock_response.status_code = 200
                mock_response._content = html_content.encode("utf-8")
                mock_response.url = url
                mock_response.headers = {"Content-Type": "text/html"}

                return mock_response

            except Exception as browser_error:
                print(f"Browser scraping failed for {url}: {browser_error}")
                # Track failed browser request
                _monitor.record_browser_request(success=False)
                print(f"Browser fallback also failed for {url}: {browser_error}")
                raise http_error

    def make_request(self, url: Optional[str] = None) -> Response:
        """
        Make an HTTP GET request to the specified URL with intelligent retry logic and monitoring.

        Args:
            url (str, optional): The URL to make the request to. If not provided, the class's URL
                attribute will be used.

        Returns:
            Response: An HTTP Response object containing the server's response to the request.

        Raises:
            HTTPException: If there are too many redirects, persistent client/server errors,
                or all retry attempts fail.
        """
        url = self.URL if not url else url
        start_time = self._get_timestamp()

        # Ensure session is initialized
        if self.session is None:
            self.session = _session_manager.get_session(self.session_id)

        def _single_request() -> Response:
            """Single request attempt with error handling and monitoring."""
            try:
                # Double-check session is available
                if self.session is None:
                    self.session = _session_manager.get_session(self.session_id)

                response: Response = self.session.get(url=url, timeout=30)
                response_time = self._get_timestamp() - start_time

                # Check for anti-bot indicators
                is_blocked = self._detect_block(response)

                if is_blocked:
                    _monitor.record_request(success=False, response_time=response_time, was_blocked=True)
                    raise HTTPException(
                        status_code=403,
                        detail=f"Anti-bot block detected for url: {url}",
                    )

                # Success - record metrics
                _monitor.record_request(success=True, response_time=response_time, was_blocked=False)

                return response

            except TooManyRedirects:
                _monitor.record_request(success=False, response_time=self._get_timestamp() - start_time)
                raise HTTPException(status_code=404, detail=f"Not found for url: {url}")
            except requests.exceptions.Timeout:
                _monitor.record_request(success=False, response_time=self._get_timestamp() - start_time)
                raise HTTPException(status_code=408, detail=f"Request timeout for url: {url}")
            except requests.exceptions.ConnectionError:
                _monitor.record_request(success=False, response_time=self._get_timestamp() - start_time)
                raise HTTPException(status_code=503, detail=f"Connection error for url: {url}")
            except Exception as e:
                _monitor.record_request(success=False, response_time=self._get_timestamp() - start_time)
                raise HTTPException(status_code=500, detail=f"Request error for url: {url}. {e}")

        # Execute with retry logic
        response = _retry_manager.execute_with_retry(_single_request)
        return response

    def _detect_block(self, response: Response) -> bool:
        """
        Detect if response indicates anti-bot blocking.

        Args:
            response: HTTP response to analyze

        Returns:
            bool: True if block is detected
        """
        text_lower = response.text.lower()

        # First check status codes - these are definitive
        if response.status_code in [403, 429, 503]:
            # For 403, check if it's actually a block page (not just a 403 with valid content)
            if response.status_code == 403:
                # If we have substantial content with transfermarkt branding, it's likely not a block
                if len(response.text) > 5000 and "transfermarkt" in text_lower:
                    return False
            return True

        # Check for suspiciously short responses without transfermarkt content
        if len(response.text) < 1000 and "transfermarkt" not in text_lower:
            return True

        # Check for explicit block messages (but only if status code suggests it)
        # These keywords alone aren't enough - they appear in normal HTML too
        explicit_block_phrases = [
            "access denied",
            "you have been blocked",
            "your access has been blocked",
            "rate limit exceeded",
            "too many requests",
        ]

        # Only flag if we find explicit block phrases AND status suggests blocking
        if response.status_code >= 400:
            for phrase in explicit_block_phrases:
                if phrase in text_lower:
                    return True

        # CAPTCHA detection - more specific
        captcha_indicators = [
            "captcha" in text_lower and ("solve" in text_lower or "verify" in text_lower),
            "recaptcha" in text_lower,
            "hcaptcha" in text_lower,
        ]
        if any(captcha_indicators):
            return True

        return False

    def _get_timestamp(self) -> float:
        """Get current timestamp for performance monitoring."""
        import time

        return time.time()

    def request_url_bsoup(self) -> BeautifulSoup:
        """
        Fetch the web page content and parse it using BeautifulSoup.
        Uses browser fallback if HTTP request fails.

        Returns:
            BeautifulSoup: A BeautifulSoup object representing the parsed web page content.

        Raises:
            HTTPException: If both HTTP and browser requests fail.
        """
        try:
            response: Response = self.make_request()
        except Exception as http_error:
            # Try browser fallback
            try:
                response = self.make_request_with_browser_fallback(use_browser=True)
            except Exception:
                # If both fail, raise the original HTTP error
                raise http_error

        return BeautifulSoup(  # noqa: E501
            markup=response.content if hasattr(response, "content") else response.text,
            features="html.parser",
        )

    @staticmethod
    def convert_bsoup_to_page(bsoup: BeautifulSoup) -> ElementTree:
        """
        Convert a BeautifulSoup object to an ElementTree.

        Args:
            bsoup (BeautifulSoup): The BeautifulSoup object representing the parsed web page content.

        Returns:
            ElementTree: An ElementTree representing the parsed web page content for further processing.

        Raises:
            HTTPException: If HTML parsing fails and returns None.
        """
        page = etree.HTML(str(bsoup))
        if page is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse HTML content from the web page",
            )
        return page

    def request_url_page(self) -> ElementTree:
        """
        Fetch the web page content, parse it using BeautifulSoup, and convert it to an ElementTree.
        Uses browser fallback if HTTP request fails.

        Returns:
            ElementTree: An ElementTree representing the parsed web page content for further
                processing.

        Raises:
            HTTPException: If both HTTP and browser requests fail.
        """
        try:
            bsoup: BeautifulSoup = self.request_url_bsoup()
        except Exception as http_error:
            # Try browser fallback
            print(f"HTTP request failed for {self.URL}, trying browser fallback: {http_error}")
            try:
                browser_response = self.make_request_with_browser_fallback(use_browser=True)
                if not browser_response or not browser_response.text:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Browser fallback returned empty content for {self.URL}",
                    )
                bsoup = BeautifulSoup(markup=browser_response.text, features="html.parser")
            except Exception as browser_error:
                print(f"Browser fallback also failed for {self.URL}: {browser_error}")
                # If both fail, raise the original HTTP error
                raise http_error

        page = self.convert_bsoup_to_page(bsoup=bsoup)
        if page is None:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse HTML content from {self.URL}",
            )
        return page

    def raise_exception_if_not_found(self, xpath: str):
        """
        Raise an exception if the specified XPath does not yield any results on the web page.

        Args:
            xpath (str): The XPath expression to query elements on the page.

        Raises:
            HTTPException: If the specified XPath query does not yield any results, indicating an invalid request.
        """
        if not self.get_text_by_xpath(xpath):
            raise HTTPException(status_code=404, detail=f"Invalid request (url: {self.URL})")

    def get_list_by_xpath(self, xpath: str, remove_empty: Optional[bool] = True) -> Optional[list]:
        """
        Extract a list of elements from the web page using the specified XPath expression.

        Args:
            xpath (str): The XPath expression to query elements on the page.
            remove_empty (bool, optional): If True, remove empty or whitespace-only elements from
                the list. Default is True.

        Returns:
            Optional[list]: A list of elements extracted from the web page based on the XPath query.
                If remove_empty is True, empty or whitespace-only elements are filtered out.

        Raises:
            HTTPException: If the page is not initialized (None).
        """
        if self.page is None:
            raise HTTPException(
                status_code=500,
                detail=f"Page not initialized. Unable to extract data from web page. URL: {self.URL}",
            )
        try:
            elements: list = self.page.xpath(xpath)
        except Exception as e:
            print(f"XPath error for {xpath} on {self.URL}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"XPath extraction failed for {xpath} on {self.URL}: {e}",
            )
        if remove_empty:
            elements_valid: list = [trim(e) for e in elements if trim(e)]
        else:
            elements_valid: list = [trim(e) for e in elements]
        return elements_valid or []

    def get_text_by_xpath(
        self,
        xpath: str,
        pos: int = 0,
        iloc: Optional[int] = None,
        iloc_from: Optional[int] = None,
        iloc_to: Optional[int] = None,
        join_str: Optional[str] = None,
    ) -> Optional[str]:
        """
        Extract text content from the web page using the specified XPath expression.

        Args:
            xpath (str): The XPath expression to query elements on the page.
            pos (int, optional): Index of the element to extract if multiple elements match the
                XPath. Default is 0.
            iloc (int, optional): Extract a single element by index, used as an alternative to 'pos'.
            iloc_from (int, optional): Extract a range of elements starting from the specified
                index (inclusive).
            iloc_to (int, optional): Extract a range of elements up to the specified
                index (exclusive).
            join_str (str, optional): If provided, join multiple text elements into a single string
                using this separator.

        Returns:
            Optional[str]: The extracted text content from the web page based on the XPath query and
                optional parameters. If no matching element is found, None is returned.

        Raises:
            HTTPException: If the page is not initialized (None).
        """
        if self.page is None:
            raise HTTPException(
                status_code=500,
                detail="Page not initialized. Unable to extract data from web page.",
            )
        element = self.page.xpath(xpath)

        if not element:
            return None

        if isinstance(element, list):
            element = [trim(e) for e in element if trim(e)]

        if isinstance(iloc, int):
            element = element[iloc]

        if isinstance(iloc_from, int) and isinstance(iloc_to, int):
            element = element[iloc_from:iloc_to]

        if isinstance(iloc_to, int):
            element = element[:iloc_to]

        if isinstance(iloc_from, int):
            element = element[iloc_from:]

        if isinstance(join_str, str):
            return join_str.join([trim(e) for e in element])

        try:
            return trim(element[pos])
        except IndexError:
            return None

    def get_last_page_number(self, xpath_base: str = "") -> int:
        """
        Retrieve the last page number for a paginated result based on the provided base XPath.

        Args:
            xpath_base (str): The base XPath for extracting page number information.

        Returns:
            int: The last page number for search results. Returns 1 if no page numbers are found.
        """

        for xpath in [Pagination.PAGE_NUMBER_LAST, Pagination.PAGE_NUMBER_ACTIVE]:
            url_page = self.get_text_by_xpath(xpath_base + xpath)
            if url_page:
                return int(url_page.split("=")[-1].split("/")[-1])
        return 1

    def rotate_session(self) -> None:
        """
        Force rotation to a new session with different fingerprint.
        Useful when encountering rate limits or blocks.
        """
        self.session_id = str(uuid.uuid4())
        self.session = _session_manager.get_session(self.session_id)

    @staticmethod
    def get_session_stats() -> Dict:
        """
        Get statistics about the current session manager state.

        Returns:
            Dict: Session statistics including active sessions, proxies, etc.
        """
        return _session_manager.get_session_stats()

    @staticmethod
    def get_retry_stats() -> Dict:
        """
        Get statistics about retry behavior.

        Returns:
            Dict: Retry configuration and statistics.
        """
        return {
            "max_attempts": _retry_manager.max_attempts,
            "base_delay": _retry_manager.base_delay,
            "max_delay": _retry_manager.max_delay,
            "exponential_base": _retry_manager.exponential_base,
            "jitter_factor": _retry_manager.jitter_factor,
        }

    @staticmethod
    def has_proxy_support() -> bool:
        """
        Check if proxy support is configured.

        Returns:
            bool: True if proxies are available, False otherwise.
        """
        return len(_session_manager.proxies) > 0

    @staticmethod
    def get_monitoring_stats() -> Dict:
        """
        Get comprehensive anti-scraping monitoring statistics.

        Returns:
            Dict: Complete monitoring data including success rates, blocks, performance metrics.
        """
        stats = _monitor.get_stats()
        stats["browser_scraping_available"] = PLAYWRIGHT_AVAILABLE and _browser_scraper is not None
        if _browser_scraper is not None:
            stats["browser_user_agents"] = len(_browser_scraper.user_agents)
            stats["browser_viewports"] = len(_browser_scraper.viewport_sizes)
        else:
            stats["browser_user_agents"] = 0
            stats["browser_viewports"] = 0
        return stats
