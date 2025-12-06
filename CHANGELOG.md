# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **National Teams Support**: Full support for national teams across all club endpoints
  - Added `isNationalTeam` boolean field to Club Profile response schema
  - Club Profile endpoint now automatically detects and indicates if a club is a national team
  - Club Players endpoint now supports fetching players from national teams
  - Club Competitions endpoint supports national teams

- **New Endpoint**: `/clubs/{club_id}/competitions`
  - Retrieves all competitions a club participates in for a given season
  - Supports both regular clubs and national teams
  - Returns competition ID, name, and URL for each competition
  - Defaults to current season if `season_id` is not provided

### Changed
- **Club Profile Schema**: Made several fields optional to accommodate national teams
  - `stadium_name`, `stadium_seats`, `current_transfer_record` are now optional
  - `squad.national_team_players` is now optional
  - `league` fields can now be `None` for national teams

- **Club Players Endpoint**: Enhanced to handle different HTML structures
  - Automatically detects national teams and uses appropriate parsing logic
  - Handles different table structures between clubs and national teams
  - Ensures all player data lists are properly aligned for correct parsing

### Technical Details
- Updated XPath expressions to support both club and national team HTML structures
- Added intelligent detection logic for national teams based on HTML structure
- Improved error handling and data validation for edge cases
- All changes maintain backward compatibility with existing club endpoints

