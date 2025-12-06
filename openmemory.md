# Transfermarkt API - Project Memory Guide

## Overview
API service til at hente data fra Transfermarkt ved hjælp af web scraping. Projektet bruger FastAPI, BeautifulSoup, og lxml til at scrape og parse HTML fra Transfermarkt.

## Architecture

### API Structure
- **FastAPI** framework med Pydantic schemas til validering
- **Router-based** struktur med separate endpoints for clubs, players, og competitions
- **Service layer** der håndterer scraping logik
- **Schema layer** der definerer data strukturer og validering

### Key Components

#### Services (`app/services/`)
- `base.py` - Base klasse `TransfermarktBase` med HTTP request og XPath extraction funktionalitet
- `clubs/profile.py` - Scraper for club/national team profiler
- `clubs/players.py` - Scraper for club spillere
- `clubs/search.py` - Club søgning
- `players/` - Spiller-relaterede services
- `competitions/` - Competition-relaterede services

#### Schemas (`app/schemas/`)
- Pydantic modeller med camelCase aliases
- Field validators til at parse strings til dates, integers, etc.
- Optional felter for data der ikke altid er tilgængelige

#### Utils (`app/utils/`)
- `xpath.py` - XPath expressions for forskellige elementer på Transfermarkt sider
- `utils.py` - Utility funktioner (trim, safe_regex, extract_from_url, etc.)
- `regex.py` - Regex patterns til data extraction

## User Defined Namespaces
- [Leave blank - user populates]

## Components

### Club Profile Service
**Location:** `app/services/clubs/profile.py`
**Purpose:** Scraper club og national team profiler fra Transfermarkt
**Key Methods:**
- `get_club_profile()` - Henter og parser alle club profile data
- Bruger XPath expressions fra `Clubs.Profile` til at extracte data
- Håndterer både klubber og national teams

**I/O:**
- Input: `club_id` (string)
- Output: Dictionary med club profile data

### Club Profile Schema
**Location:** `app/schemas/clubs/profile.py`
**Purpose:** Pydantic model til validering af club profile data
**Key Fields:**
- `stadium_name`, `stadium_seats`, `current_transfer_record` - Optional (kan være None for national teams)
- `squad.national_team_players` - Optional (kan være None for national teams)
- `league` - Optional (kan være None eller have None værdier)

## Patterns

### National Teams Support
**Issue:** National teams har ikke samme HTML struktur som klubber - mangler felter som stadium, transfer record, etc.
**Solution:** Gjorde relevante felter Optional i schemaet:
- `stadium_name: Optional[str] = None`
- `stadium_seats: Optional[int] = None`
- `current_transfer_record: Optional[int] = None`
- `squad.national_team_players: Optional[int] = None`

**Implementation:** Schema opdateret i `app/schemas/clubs/profile.py` til at understøtte både klubber og national teams.

### Error Handling
- `get_text_by_xpath()` returnerer `None` hvis element ikke findes
- `get_text_by_xpath()` og `get_list_by_xpath()` rejser `HTTPException` hvis `self.page` er `None` (page ikke initialiseret)
- `convert_bsoup_to_page()` rejser `HTTPException` hvis HTML parsing fejler og returnerer `None`
- `remove_str()` håndterer None korrekt (returnerer None hvis input ikke er string)
- Pydantic validators håndterer None værdier korrekt når felter er Optional

### Anti-Bot Protection
- **SmartSessionManager**: Avanceret session håndtering med User-Agent rotation (12+ forskellige UAs)
- **RetryManager**: Intelligent retry logic med exponential backoff og jitter
- **Proxy Support**: Residential proxy integration (Bright Data/Oxylabs kompatibel)
- Browser-lignende headers med dynamisk Sec-Fetch-* værdier
- Session persistence med configurable timeouts
- Railway-optimerede environment variables

**Implementerede komponenter:**
- `SmartSessionManager` klasse med session rotation og cleanup
- `RetryManager` klasse med exponential backoff (1-3 sekunder delays)
- `AntiScrapingMonitor` klasse med comprehensive tracking
- `PlaywrightBrowserScraper` klasse med real browser simulation
- Railway environment variable support i `settings.py`
- Proxy konfiguration klar (men deaktiveret - kører proxy-frit)
- Browser fingerprinting avoidance og behavioral simulation
- FastAPI monitoring endpoints: `/monitoring/anti-scraping`, `/health`, `/test/browser-scraping`
- Success rate tracking, block detection, performance metrics
- JavaScript execution capabilities og Cloudflare bypass

**Konfiguration:**
- Se `RAILWAY_ENV_CONFIG.md` for komplet setup guide
- Environment variables for session timeouts, delays, og proxy credentials
- Understøtter op til 10 proxy endpoints
- Jitter og randomization for anti-detection

### Club Competitions Service
**Location:** `app/services/clubs/competitions.py`
**Purpose:** Scraper competitions som en klub deltager i fra Transfermarkt's spielplan side
**Key Methods:**
- `get_club_competitions()` - Henter og parser alle competitions klubben deltager i for en given sæson
- Bruger XPath expressions fra `Clubs.Competitions` til at extracte data fra Record tabellen
- Default season_id er current year hvis ikke angivet

**I/O:**
- Input: `club_id` (string), `season_id` (string, optional)
- Output: Dictionary med club ID, season ID, og liste af competitions

**URL Pattern:**
- `https://www.transfermarkt.us/-/spielplan/verein/{club_id}/plus/0?saison_id={season_id}`

