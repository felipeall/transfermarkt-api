class Players:
    class Injuries:
        RESULTS = "//div[@id='yw1']//tbody//tr"
        SEASONS = ".//td[1]//text()"
        INJURY = ".//td[2]//text()"
        FROM = ".//td[3]//text()"
        UNTIL = ".//td[4]//text()"
        DAYS = ".//td[5]//text()"
        GAMES_MISSED = ".//td[6]//span//text()"
        GAMES_MISSED_CLUBS_URLS = ".//td[6]//a//@href"

    class JerseyNumbers:
        HEADERS = "//table[@class='items']//thead//tr//@title"
        SEASONS = "//table[@class='items']//td[@class='zentriert']//text()"
        CLUBS_URLS = "//table[@class='items']//td[@class='hauptlink no-border-links']//a//@href"
        DATA = "//table[@class='items']//td[@class='zentriert hauptlink']//text()"

    class Profile:
        ID = "//tm-subnavigation[@controller='spieler']//@id"
        URL = "//link[@rel='canonical']//@href"
        NAME = "//h1[@class='data-header__headline-wrapper']/descendant-or-self::*[not(self::span)]/text()"
        DESCRIPTION = "//meta[@name='description']//@content"
        IMAGE_URL = "//div[@id='fotoauswahlOeffnen']//img//@src"
        SHIRT_NUMBER = "//span[@class='data-header__shirt-number']//text()"
        CURRENT_CLUB_NAME = "//span[@class='data-header__club']//text()"
        CURRENT_CLUB_URL = "//span[@class='data-header__club']//a//@href"
        CURRENT_CLUB_JOINED = "//span[contains(text(),'Joined')]//following::span[1]//text()"
        LAST_CLUB_NAME = "//span[contains(text(),'Last club:')]//span//a//@title"
        LAST_CLUB_URL = "//span[contains(text(),'Last club:')]//span//a//@href"
        MOST_GAMES_FOR_CLUB_NAME = "//span[contains(text(),'Most games for:')]//span//a//text()"
        RETIRED_SINCE_DATE = "//span[contains(text(),'Retired since:')]//span//text()"
        CURRENT_CLUB_CONTRACT_EXPIRES = "//span[contains(text(),'Contract expires')]//following::span[1]//text()"
        CURRENT_CLUB_CONTRACT_OPTION = "//span[contains(text(),'Contract option:')]//following::span[1]//text()"
        NAME_IN_HOME_COUNTRY = "//span[text()='Name in home country:']//following::span[1]//text()"
        FULL_NAME = "//span[text()='Full name:']//following::span[1]//text()"
        DATE_OF_BIRTH_AGE = "//span[@itemprop='birthDate']//text()"
        PLACE_OF_BIRTH_CITY = "//span[contains(text(),'Place of birth')]//following::span[1]//text()"
        PLACE_OF_BIRTH_COUNTRY = "//span[contains(text(),'Place of birth')]//following::span[1]//img//@title"
        HEIGHT = "//span[text()='Height:']//following::span[1]//text()"
        CITIZENSHIP = "//span[text()='Citizenship:']//following::span[1]//text()"
        POSITION = "//span[text()='Position:']//following::span[1]//text()"
        POSITION_MAIN = "//dt[contains(text(),'Main position:')]//following::dd[1]//text()"
        POSITION_OTHER = "//dt[contains(text(),'Other position:')]//following::dd//text()"
        FOOT = "//span[text()='Foot:']//following::span[1]//text()"
        MARKET_VALUE = "//a[@class='data-header__market-value-wrapper']//text()"
        AGENT_NAME = "//span[text()='Player agent:']//following::span[1]//text()"
        AGENT_URL = "//span[text()='Player agent:']//following::span[1]//a//@href"
        OUTFITTER = "//span[contains(text(),'Outfitter:')]//following::span[1]//text()"
        SOCIAL_MEDIA = "//div[@class='social-media-toolbar__icons']//@href"
        TRAINER_PROFILE_URL = "//a[@class='data-header__box--link']//@href"
        TRAINER_PROFILE_POSITION = "//div[@class='dataProfileDaten']//span[1]//text()"
        RELATIVES = (
            "//div[@class='box tm-player-additional-data']"
            "//a[contains(@href, 'profil/spieler') or contains(@href, 'profil/trainer')]"
        )
        RELATIVE_URL = ".//@href"
        RELATIVE_NAME = ".//text()"

    class Search:
        # Updated for new Transfermarkt HTML structure (2024)
        BASE = "//div[@id='yw0']"  # Player search results table container
        RESULTS = BASE + "//table[@class='items']//tbody//tr[@class='odd' or @class='even']"
        # Player names: td > table.inline-table > tbody > tr > td.hauptlink > a @title
        ID = ".//td//table[@class='inline-table']//td[@class='hauptlink']//a//@href"
        NAME = ".//td//table[@class='inline-table']//td[@class='hauptlink']//a//@title"
        # Position: td.zentriert (first zentriert column in this row)
        POSITION = ".//td[@class='zentriert'][1]//text()"
        # Club name: td.zentriert > a > img.tiny_wappen @title (in this row)
        CLUB_NAME = ".//td[@class='zentriert']//img[@class='tiny_wappen']//@title"
        CLUB_IMAGE = ".//td[@class='zentriert']//img[@class='tiny_wappen']//@src"
        # Age: td.zentriert (second zentriert column in this row)
        AGE = ".//td[@class='zentriert'][2]//text()"
        # Nationalities: td.zentriert > img.flaggenrahmen @title (relative to row, can be multiple)
        NATIONALITIES = ".//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        # Market value: td.rechts.hauptlink (in this row)
        MARKET_VALUE = ".//td[@class='rechts hauptlink']//text()"
        FOUND = BASE + "//text()"

    class MarketValue:
        URL = "//a[@class='data-header__market-value-wrapper']//@href"
        CURRENT = (
            "//a[@class='data-header__market-value-wrapper']//text()[not(parent::p/@class='data-header__last-update')]"
        )
        HIGHCHARTS = "//script[@type='text/javascript'][text()[contains(.,'Highcharts.Chart')]]//text()"
        RANKINGS_NAMES = "//h3[@class='quick-fact__headline']//text()"
        RANKINGS_POSITIONS = "//span[contains(@class, 'quick-fact__content--large')]//text()"

    class Transfers:
        YOUTH_CLUBS = (
            "//div[@class='box tm-player-additional-data'][descendant::*[contains(text(), 'Youth')]]"
            "//div[@class='content']//text()"
        )

    class Stats:
        ROWS = "//table[@class='items']//tbody//tr"
        HEADERS = "//table[@class='items']//thead//tr//@title"
        COMPETITIONS_URLS = "//table[@class='items']//td[@class='hauptlink no-border-links']//a//@href"
        CLUBS_URLS = "//table[@class='items']//td[@class='hauptlink no-border-rechts zentriert']//a//@href"
        DATA = ".//text()"

    class Achievements:
        ACHIEVEMENTS = "//div[@class='box'][descendant::table[@class='auflistung']]"
        TITLE = ".//h2//text()"
        DETAILS = ".//table[@class='auflistung']//tr"
        SEASON = ".//td[contains(@class, 'erfolg_table_saison')]//text()"
        CLUB_NAME = ".//a[contains(@href, '/verein/')][not(img)]/@title"
        CLUB_URL = ".//a[contains(@href, '/verein/')][not(img)]/@href"
        COMPETITION_NAME = ".//a[contains(@href, '/wettbewerb/') or contains(@href, '/pokalwettbewerb/')]/text()"
        COMPETITION_URL = ".//a[contains(@href, '/wettbewerb/') or contains(@href, '/pokalwettbewerb/')]/@href"


class Clubs:
    class Profile:
        # Updated for new Transfermarkt HTML structure (2024)
        URL = "//link[@rel='canonical']//@href"
        NAME = "//div[@class='data-header__headline-container']//h1//text()"
        NAME_OFFICIAL = "//th[text()='Official club name:']//following::td[1]//text()"
        IMAGE = "//div[@class='data-header__box--big']//img//@src"
        LEGAL_FORM = "//th[text()='Legal form:']//following::td[1]//text()"
        ADDRESS_LINE_1 = "//th[text()='Address:']//following::td[1]//text()"
        ADDRESS_LINE_2 = "//th[text()='Address:']//following::td[2]//text()"
        ADDRESS_LINE_3 = "//th[text()='Address:']//following::td[3]//text()"
        TEL = "//th[text()='Tel:']//following::td[1]//text()"
        FAX = "//th[text()='Fax:']//following::td[1]//text()"
        WEBSITE = "//th[text()='Website:']//following::td[1]//text()"
        FOUNDED_ON = "//th[text()='Founded:']//following::td[1]//text()"
        MEMBERS = "//th[text()='Members:']//following::td[1]//text()"
        MEMBERS_DATE = "//th[text()='Members:']//following::td[1]//span//text()"
        OTHER_SPORTS = "//th[text()='Other sports:']//following::td[1]//text()"
        COLORS = "//p[@class='vereinsfarbe']//@style"
        STADIUM_NAME = "//li[contains(text(), 'Stadium:')]//span//a//text()"
        STADIUM_SEATS = "//li[contains(text(), 'Stadium:')]//span//span//text()"
        TRANSFER_RECORD = "//li[contains(text(), 'Current transfer record:')]//a//text()"
        MARKET_VALUE = "//a[@class='data-header__market-value-wrapper']//text()"
        CONFEDERATION = "//li[contains(text(), 'Konföderation:')]//span//text()"
        RANKING = "//li[contains(text(), 'FIFA World Ranking:')]//span//a//text()"
        SQUAD_SIZE = "//li[contains(text(), 'Squad size:')]//span//text()"
        SQUAD_AVG_AGE = "//li[contains(text(), 'Average age:')]//span//text()"
        SQUAD_FOREIGNERS = "//li[contains(text(), 'Foreigners:')]//span[1]//a//text()"
        SQUAD_NATIONAL_PLAYERS = "//li[contains(text(), 'National team players:')]//span//a//text()"
        LEAGUE_ID = "//span[@itemprop='affiliation']//a//@href"
        LEAGUE_NAME = "//span[@itemprop='affiliation']//a//text()"
        LEAGUE_COUNTRY_ID = "//div[@class='data-header__club-info']//img[contains(@class, 'flaggenrahmen')]//@data-src"
        LEAGUE_COUNTRY_NAME = "//div[@class='data-header__club-info']//img[contains(@class, 'flaggenrahmen')]//@title"
        LEAGUE_TIER = "//div[@class='data-header__club-info']//strong//text()//following::span[1]/a/text()[2]"
        CRESTS_HISTORICAL = "//div[@class='wappen-datenfakten-wappen']//@src"

    class Search:
        # Updated for new Transfermarkt HTML structure (2024)
        BASE = "//div[@id='yw1']"  # Club search results table container
        RESULTS = BASE + "//table[@class='items']//tbody//tr[@class='odd' or @class='even']"
        # Club names: td > table.inline-table > tbody > tr > td.hauptlink > a @title
        NAMES = RESULTS + "//td//table[@class='inline-table']//td[@class='hauptlink']//a//@title"
        # Club URLs: td > table.inline-table > tbody > tr > td.hauptlink > a @href
        URLS = RESULTS + "//td//table[@class='inline-table']//td[@class='hauptlink']//a//@href"
        # Countries: td.zentriert > img.flaggenrahmen @title
        COUNTRIES = RESULTS + "//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        # Squad sizes: td.zentriert > a (contains the number)
        SQUADS = RESULTS + "//td[@class='zentriert']//a//text()"
        # Market values: td.rechts (contains € values)
        MARKET_VALUES = RESULTS + "//td[@class='rechts']//text()"

    class Players:
        # Updated for new Transfermarkt HTML structure (2024)
        BASE = "//div[@id='yw1']"  # Club players table container
        RESULTS = BASE + "//table[@class='items']//tbody//tr[@class='odd' or @class='even']"
        PAST_FLAG = BASE + "//thead//text()"
        CLUB_NAME = "//div[@class='data-header__headline-container']//h1//text()"
        CLUB_URL = "//li[@id='overview']//@href"
        PAGE_NATIONALITIES = RESULTS + "//td[img[@class='flaggenrahmen']]"
        PAGE_INFOS = RESULTS + "//td[@class='posrela']"
        # Player names: td.posrela > table.inline-table > tbody > tr > td.hauptlink > a
        NAMES = RESULTS + "//td[@class='posrela']//table[@class='inline-table']//td[@class='hauptlink']//a//text()"
        # Player URLs: td.posrela > table.inline-table > tbody > tr > td.hauptlink > a @href
        URLS = RESULTS + "//td[@class='posrela']//table[@class='inline-table']//td[@class='hauptlink']//a//@href"
        # Positions: td.zentriert (first zentriert column after posrela)
        # Note: First zentriert might have additional classes
        POSITIONS = RESULTS + "//td[contains(@class, 'zentriert')][1]//text()"
        # Age: DOB/Age is in zentriert column that contains date pattern (DD/MM/YYYY)
        # Match td with zentriert class containing date pattern
        DOB_AGE = RESULTS + "//td[@class='zentriert' and contains(text(), '/') and string-length(text()) > 8]//text()"
        # Nationalities: td.zentriert > img.flaggenrahmen @title
        NATIONALITIES = RESULTS + "//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        JOINED = ".//span/node()/@title"
        SIGNED_FROM = ".//a//img//@title"
        # Market values: td.rechts.hauptlink
        MARKET_VALUES = RESULTS + "//td[@class='rechts hauptlink']//text()"
        STATUSES = ".//td[@class='hauptlink']//span//@title"
        JOINED_ON = ".//text()"

        class Present:
            # Contract: td.zentriert (fourth zentriert column)
            # Using BASE + table path since RESULTS is not accessible in nested class
            PAGE_SIGNED_FROM = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][3]"  # noqa: E501
            PAGE_JOINED_ON = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][4]"  # noqa: E501
            HEIGHTS = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][5]//text()"  # noqa: E501
            FOOTS = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][6]//text()"  # noqa: E501
            CONTRACTS = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][4]//text()"  # noqa: E501

        class Past:
            PAGE_SIGNED_FROM = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][3]"  # noqa: E501
            PAGE_JOINED_ON = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][4]"  # noqa: E501
            CURRENT_CLUB = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][1]//img//@title"  # noqa: E501
            HEIGHTS = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][5]//text()"  # noqa: E501
            FOOTS = "//div[@id='yw1']//table[@class='items']//tbody//tr[@class='odd' or @class='even']//td[@class='zentriert'][6]//text()"  # noqa: E501

    class Competitions:
        RECORD_HEADING = "//h2[contains(text(), 'Record')]"
        RECORD_TABLE = "//h2[contains(text(), 'Record')]/following::table[1]"
        COMPETITION_LINKS = ".//a[contains(@href, '/wettbewerb/') or contains(@href, '/pokalwettbewerb/')]"
        COMPETITION_NAME = ".//a[contains(@href, '/wettbewerb/') or contains(@href, '/pokalwettbewerb/')]//text()"
        COMPETITION_URL = ".//a[contains(@href, '/wettbewerb/') or contains(@href, '/pokalwettbewerb/')]//@href"


class Competitions:
    class Profile:
        # Updated for new Transfermarkt HTML structure (2024)
        # Using more robust fallbacks from main branch
        URL = "//link[@rel='canonical']//@href"
        NAME = (
            "//div[@class='data-header__headline-container']//h1//text() | "
            "//h1[contains(@class, 'content-box-headline')]//text() | "
            "//div[contains(@class, 'data-header')]//h1//text() | "
            "//h1[not(contains(text(), 'Participating teams'))]//text()"
        )
        SEASON_DROPDOWN = (
            "//table[contains(., 'Filter by season:')]"
            "//td[contains(., 'Filter by season:')]/following-sibling::td[1] | "
            "//table//td[contains(text(), 'Filter by season:')]/following-sibling::td[1]"
        )
        SEASON_OPTIONS = (
            ".//li[contains(@class, 'list-item')]//text() | "
            ".//li//text() | "
            ".//ul//li//text() | "
            ".//list//listitem//text() | "
            ".//text()[normalize-space()]"
        )
        SEASON_SELECTED = ".//a[contains(@href, 'javascript:void(0)')]//text()"
        SEASON_TABLE_CELL = (
            "//table[contains(., 'Filter by season:')]"
            "//td[contains(., 'Filter by season:')]/following-sibling::td[1]//text()"
        )

    class Search:
        # Updated for new Transfermarkt HTML structure (2024)
        BASE = "//div[@id='yw1']"  # Competition search results table container
        RESULTS = BASE + "//table[@class='items']//tbody//tr[@class='odd' or @class='even']"
        # Competition URLs: td > a @href (direct link, not in inline-table)
        URLS = RESULTS + "//td//a[contains(@href, '/wettbewerb/')]//@href"
        # Competition names: td > a @title
        NAMES = RESULTS + "//td//a[contains(@href, '/wettbewerb/')]//@title"
        # Countries: td.zentriert > img.flaggenrahmen @title (first zentriert column)
        COUNTRIES = RESULTS + "//td[@class='zentriert'][1]//img[@class='flaggenrahmen']//@title"
        # Clubs: td.zentriert (second zentriert column, contains number)
        CLUBS = RESULTS + "//td[@class='zentriert'][2]//text()"
        # Players: td.rechts (contains player count)
        PLAYERS = RESULTS + "//td[@class='rechts']//text()"
        # Total market values: td.zentriert (third zentriert column)
        TOTAL_MARKET_VALUES = RESULTS + "//td[@class='zentriert'][3]//text()"
        # Mean market values: td.zentriert (fourth zentriert column)
        MEAN_MARKET_VALUES = RESULTS + "//td[@class='zentriert'][4]//text()"
        # Continents: td.zentriert (fifth zentriert column)
        CONTINENTS = RESULTS + "//td[@class='zentriert'][5]//text()"

    class Clubs:
        # Match both regular clubs and national teams
        # Regular clubs: td[@class='hauptlink no-border-links']
        # National teams may have different class or structure, so we use a more general approach
        # Match any td with hauptlink class that contains links to clubs or national teams
        # Use union to match both the original pattern and national teams
        URLS = (
            "//td[@class='hauptlink no-border-links']//a[1]//@href | "
            "//td[contains(@class, 'hauptlink')]//a[contains(@href, '/nationalmannschaft/')]//@href"
        )
        NAMES = (
            "//td[@class='hauptlink no-border-links']//a//text() | "
            "//td[contains(@class, 'hauptlink')]//a[contains(@href, '/nationalmannschaft/')]//text()"
        )
        # XPath for participants table on /teilnehmer/ pages (national team competitions)
        # Only get teams from the first table (actual participants), not from "not qualified" tables
        # The participants table comes after h2 with "Clubs starting into tournament at a later point"
        # Filter to only get rows that have team links (exclude header row)
        PARTICIPANTS_URLS = (
            "//h2[contains(text(), 'Clubs starting into tournament')]/following::table[1]"
            "//tr[.//a[contains(@href, '/verein/') or contains(@href, '/nationalmannschaft/')]]"
            "//td[@class='hauptlink no-border-links']//a[1]//@href | "
            "//h2[contains(text(), 'Clubs starting into tournament')]/following::table[1]"
            "//tr[.//a[contains(@href, '/verein/') or contains(@href, '/nationalmannschaft/')]]"
            "//td[contains(@class, 'hauptlink')]//a["
            "contains(@href, '/nationalmannschaft/') or contains(@href, '/verein/')]//@href"
        )
        PARTICIPANTS_NAMES = (
            "//h2[contains(text(), 'Clubs starting into tournament')]/following::table[1]"
            "//tr[.//a[contains(@href, '/verein/') or contains(@href, '/nationalmannschaft/')]]"
            "//td[@class='hauptlink no-border-links']//a//text() | "
            "//h2[contains(text(), 'Clubs starting into tournament')]/following::table[1]"
            "//tr[.//a[contains(@href, '/verein/') or contains(@href, '/nationalmannschaft/')]]"
            "//td[contains(@class, 'hauptlink')]//a["
            "contains(@href, '/nationalmannschaft/') or contains(@href, '/verein/')]//text()"
        )


class Pagination:
    PAGE_NUMBER_LAST = "//li[contains(@class, 'list-item--icon-last-page')]//@href"
    PAGE_NUMBER_ACTIVE = "//li[contains(@class, 'list-item--active')]//@href"
