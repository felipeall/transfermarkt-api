# Railway Environment Variables Configuration

Dette dokument beskriver de environment variables der skal sættes i Railway for optimal anti-scraping beskyttelse.

## Anti-Scraping Konfiguration

### Session Management
```bash
SESSION_TIMEOUT=3600          # Session timeout i sekunder (1 time)
MAX_SESSIONS=50               # Maximum antal samtidige sessions
MAX_CONCURRENT_REQUESTS=10    # Maximum samtidige requests per session
```

### Request Delays (Anti-Detection)
```bash
REQUEST_DELAY_MIN=1.0         # Minimum delay mellem requests (sekunder)
REQUEST_DELAY_MAX=3.0         # Maximum delay mellem requests (sekunder)
ENABLE_BEHAVIORAL_SIMULATION=false  # Behavioral simulation (kommende feature)
```

### Rate Limiting (Eksisterende)
```bash
RATE_LIMITING_ENABLE=false
RATE_LIMITING_FREQUENCY=2/3seconds
```

## Proxy Konfiguration

### Bright Data / Oxylabs Residential Proxies
```bash
PROXY_HOST=your-proxy-host.brightdata.com
PROXY_PORT=22225
PROXY_USERNAME=your-brightdata-username
PROXY_PASSWORD=your-brightdata-password
```

### Alternative: Flere Proxy URLs
```bash
PROXY_URL_1=http://username:password@proxy1.example.com:8080
PROXY_URL_2=http://username:password@proxy2.example.com:8080
# ... op til PROXY_URL_10
```

## Browser Scraping Konfiguration

### Playwright Browser Settings
```bash
ENABLE_BROWSER_SCRAPING=true    # Aktiver browser fallback
BROWSER_TIMEOUT=30000           # Timeout i millisekunder
BROWSER_HEADLESS=true          # Kør browser i headless mode
```

## Eksisterende Konfiguration (Tournament Sizes)

```bash
TOURNAMENT_SIZE_FIWC=32
TOURNAMENT_SIZE_EURO=24
TOURNAMENT_SIZE_COPA=12
TOURNAMENT_SIZE_AFAC=24
TOURNAMENT_SIZE_GOCU=16
TOURNAMENT_SIZE_AFCN=24
```

## Implementerings Guide

1. **Start med basis konfiguration** (uden proxies)
2. **Monitor performance** med de nye endpoints
3. **Juster delays** baseret på success rates
4. **Track blokeringer** via monitoring data

## Monitoring Endpoints

API'en inkluderer nu omfattende monitoring:

### `/health`
- **Formål:** Basic health check
- **Returnerer:** Service status

### `/monitoring/anti-scraping`
- **Formål:** Komplet anti-scraping statistik
- **Målinger:**
  - Success rate (%)
  - Blokeringer detekteret
  - Gennemsnitlig response time
  - Retries performed
  - Sessions created
  - Uptime

### `/monitoring/session`
- **Formål:** Session manager statistik
- **Målinger:** Aktive/expired sessions, proxies, user agents

### `/monitoring/retry`
- **Formål:** Retry konfiguration
- **Målinger:** Retry settings og performance

### Eksempel på monitoring data:
```json
{
  "uptime_seconds": 3600.5,
  "requests_total": 150,
  "requests_successful": 142,
  "success_rate_percent": 94.67,
  "blocks_detected": 3,
  "block_rate_percent": 2.0,
  "avg_response_time_seconds": 1.234,
  "session_manager_stats": {
    "active_sessions": 5,
    "user_agents_available": 12
  }
}
```

## Monitoring

API'en inkluderer nu session statistik der kan tilgås via:
- `TransfermarktBase.get_session_stats()` - Python API
- Kan integreres som endpoint for monitoring

## Proxy Services Anbefalinger

1. **Bright Data (Oxylabs)** - Bedste residential proxies (~$500/måned)
2. **Smart Proxy** - Billigere alternativ (~$300/måned)
3. **ProxyMesh** - God til testing (~$100/måned)

Start med en måned og test før permanent opsætning.
