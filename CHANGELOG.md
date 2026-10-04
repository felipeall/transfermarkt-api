# Changelog

## Unreleased

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
