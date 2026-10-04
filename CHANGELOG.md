# Changelog

## 4.2.0 — 2026-10-04

### Added

- `/games/{game_id}`: each side has `stats`, the team statistics upstream records for the match (possession, shots on/off target and blocked, passes and accurate passes, tackles and tackles won, clearances, saves, offsides, corners, fouls committed and suffered, cards, penalties won and saved, own goals). Null when upstream has none, which is common for older matches and smaller competitions.
- `/players/{player_id}/matches`: each match adds the player's `shirtNumber`, `isCaptain`, `position`, `substitutedInMinute`, `substitutedOutMinute` and `teamPoints`, plus detailed stats when recorded (`shots`, `shotsOnTarget`, `passes`, `accuratePasses`, `tackles`, `tacklesWon`, `foulsCommitted`, `foulsSuffered`, `offsides`, `ownGoals`, `penaltyGoals`, `penaltiesMissed`, `penaltiesSaved`). They are null when not recorded, which is common before 2018.
- Club profiles add `shortName`, `abbreviation`, `clubCode`, and `historicalNames` with season IDs. `squad` adds `domesticPlayers`, `averageMarketValue`, `acquisitionValue`, `top18PlayersMarketValue` and `top18SharePercentage`. Domestic players are those with the club country's nationality, not a count of locally trained players; acquisition value is the cost of the current squad, not all historical transfer spending.
- Club profiles add `stadium`: address, country, coordinates, construction and renovation years, pitch dimensions and surface, capacity (including international capacity), website and images. `stadiumName` and `stadiumSeats` remain available. Missing stadiums and unavailable details are null.
- Club squads add each player's `shirtNumber` and `isCaptain` from the selected season's squad, including past seasons and players whose individual record is missing.
- Player transfers add `age`, `contractUntil` (the agreed contract end date) and `remainingContractDays` (the remaining contract at the time of the transfer). `clubFrom` and `clubTo` add country IDs and names and `league` (ID and name), using the country and league recorded for that transfer rather than the club's current league. Missing data stays null.

## 4.1.0 — 2026-10-04

### Added

- `GET /games/{game_id}`: a match with competition, season, matchday, kickoff, stadium, attendance, score, formations, coaches, starting lineups, substitutes, and goals (with assist), cards and substitutions in match order (#112).
- `GET /players/{player_id}/matches`: past matches of the player's teams, most recent first, 50 per page, optionally for one season. Each match gives the opponent, venue, result and the player's part: played, on the bench, not in the squad, injured or absent, plus minutes, goals, assists and cards (#112). Transfermarkt's API has no fixture list, so upcoming matches are not available.
- `GET /countries/` lists country IDs and metadata (name, FIFA code, confederation, flag, historical status) (#130).
- `GET /clubs/?country_id={id}` lists the clubs Transfermarkt has for a country. The list is incomplete upstream: youth and national teams and some senior clubs are missing, with no pagination or season filter (#130, partly addresses #56).
- Club squads include each player's `imageUrl` (from #114).
- Player transfers include `transferType`: `transfer`, `freeTransfer`, `internal` (youth or reserve team to first team, and similar), `loan` or `endOfLoan`. An unknown fee stays a `transfer` with a null `fee` (from #98).
- Player stats include `goalsConceded` and `cleanSheets`, computed as on the website: goals conceded while the player was on the pitch, and matches played in which the opponent did not score. They are returned for every player, although the website shows them only for goalkeepers (from #108).
- Player profiles include:
  - `dateOfDeath`;
  - `position.group` (Goalkeeper, Defender, Midfielder or Striker);
  - `club.isCaptain` and `club.lastContractRenewal`;
  - `nationalTeam` (`id`, `name`, `shirtNumber`, `isCaptain`, `debut`);
  - `marketValueDetails`: `lastUpdated`, `trend` (`increased`, `decreased` or `unchanged`), `previous` and `highest`, each with its value and date.

## 4.0.4 — 2026-10-04

### Fixed

- The interactive docs failed to load their schema on the hosted API: opening `/` takes three requests (`/`, `/docs`, `/openapi.json`), and the third got 429. The docs pages and `/openapi.json` are no longer rate limited, like `/health`. API routes still share one budget per client IP (#145).

## 4.0.3 — 2026-10-04

### Changed

- Direct dependencies are pinned to exact versions, all at their latest releases (#143).
- The Docker image is pinned to `python:3.12.15-slim-trixie` and builds with uv `0.12.23`. uv is mounted only while dependencies are installed, so it is no longer in the final image (#143).
- CI uses uv `0.12.23`, `astral-sh/setup-uv` `v10.2.0` and `actions/checkout` `v7.0.1` (#143, #144).

## 4.0.2 — 2026-10-04

### Changed

- The hosted API caps each Fly machine at 25 requests in flight (#139). Extra requests are queued or refused by the Fly proxy instead of hanging the app.
- Each request is logged once with the client IP from `Fly-Client-IP`, the method, the path and the status (#140). uvicorn's access log, which showed the Fly proxy's address, is turned off.

### Fixed

- Rate limiting never applied to API routes. slowapi could not match routes from included routers on FastAPI 0.142, and counted each URL separately, so only `/`, `/docs` and `/openapi.json` were ever limited. slowapi is replaced by a small middleware on `limits`: one budget per client IP across all routes, `/health` excluded, and 429 responses carry `Retry-After` (#141, #142).

## 4.0.1 — 2026-10-04

### Fixed

- `page_number` below 1 now answers 422. Before, it returned records from the end of the list.
- Club squads no longer fail with 500 when the current squad lists members that are not of type `current`.
- National-team club profiles resolve `confederation` when upstream sends the country ID as a string.
- The hosted API is rate limited per client IP, as the README says. Rate-limit keys come from `Fly-Client-IP`, so a spoofed `X-Forwarded-For` no longer bypasses them; `/health` is exempt.

## 4.0.0 — 2026-10-04

Data now comes from Transfermarkt's JSON API (`tmapi.transfermarkt.technology`) instead of scraped HTML pages. The website blocks most cloud and datacenter IPs, which made v3 return errors on hosted deployments (#109, #110, #117, #121).

### Fixed

- Dates were parsed month-first after the website switched to `dd/mm/yyyy` (#111). Affected: birth dates, market-value history, transfer dates, `retiredSince`, squad `joinedOn`. All dates now come from ISO fields.
- Player profiles were missing `dateOfBirth` and `age`.
- Player stats were always empty, because the website now renders them client-side. Stats are aggregated from match data using the website's own rules.
- Club profiles failed with 500 when stadium, league or transfer data was missing (#106, #107).
- Upstream failures (blocked or empty pages) returned `500`. They now return deliberate errors: `404`, `502`, `503`, `504`.
- Money values are exact instead of parsed from rounded display strings.
- Squad `signedFrom` no longer contains parsing artefacts.

### Added

- New endpoints:
  - `GET /players/{id}/national_career` (#73)
  - `GET /players/{id}/absences`
  - `GET /clubs/{id}/achievements`
  - `GET /coaches/search/{name}`
  - `GET /coaches/{id}/profile`
  - `GET /competitions/{id}/table`
  - `GET /competitions/{id}/seasons`
- Club profile: `coach` (current head coach and start date).
- Stats: `secondYellowCards`.
- Club squad: `signedFrom` and `joinedOn` for past seasons, from transfer history.
- Club profile: `updatedAt`.
- Response caching, an upstream concurrency cap and request timeouts (configurable, see README).

### Changed (breaking)

- Fields without an upstream value are returned as `null` instead of being omitted. Many fields are now nullable.
- Market value `0` (no valuation) is returned as `null`.
- Club names are the clubs' current full names everywhere (e.g. `Paris Saint-Germain` instead of `PSG`).
- Stats `seasonId` is the season start year (`"2014"` for 14/15). Stats only cover club competitions; national-team matches are excluded, as on the website's detailed stats page.
- Club squad for a past season: `age`, `contract` and `marketValue` are `null` instead of a value of uncertain date.
- Club profile `league.countryId` is Transfermarkt's country ID (Spain: `157`).
- Achievements also list participations, runner-up and third places. Every v3 title is still present with the same count. Each detail now has both `club` and `competition` when known.
- Market value `ranking` only has the `Worldwide` key; position, club and country rankings have no JSON source.
- `updatedAt` is when the data was fetched from Transfermarkt (oldest fetch when served from cache), not when the response was built.

### Removed (no data source in the JSON API)

- `GET /players/{id}/jersey_numbers` returns `501`.
- Player profile: `description`, `socialMedia`, `trainerProfile`, `relatives`, `club.mostGamesFor`.
- Market value: rankings other than `Worldwide`.
- Injuries: `gamesMissedClubs`.
- Club squad: `status`, `joined`.
- Club profile: `legalForm`, `tel`, `fax`, `website`, `foundedOn`, `members`, `membersDate`, `otherSports`, `fifaWorldRanking`, `currentTransferRecord`.

### Known limitations

- Past-season squads omit some youth call-ups and players who left mid-season (#79).
- The JSON API is internal and undocumented; it can change without notice.

### Development

- uv and Python 3.12; Poetry and `requirements.txt` removed.
- Offline test suite with recorded upstream responses; live smoke tests with `pytest -m live`.
- CI runs lint and tests; deploys require passing checks.

### Thanks

Superseded pull requests that identified these problems: #113 and #123 (date parsing), #101 and #108 (stats), #98 (transfers), #87 (tests).
