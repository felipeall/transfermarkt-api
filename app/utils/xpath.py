class Players:
    class Profile:
        ID = "//div[@data-action='profil']//@data-id"
        URL = "//a[@class='tm-subnav-item megamenu']//@href"
        NAME = "//h1[@class='data-header__headline-wrapper']//strong//text()"
        DESCRIPTION = "//meta[@name='description']//@content"
        IMAGE_URL = "//div[@id='fotoauswahlOeffnen']//img//@src"
        SHIRT_NUMBER = "//span[@class='data-header__shirt-number']//text()"
        CURRENT_CLUB_NAME = "//span[@class='data-header__club']//text()"
        CURRENT_CLUB_URL = "//span[@class='data-header__club']//a//@href"
        CURRENT_CLUB_JOINED = "//span[text()='Joined: ']//span//text()"
        LAST_CLUB_NAME = "//span[contains(text(),'Last club:')]//span//a//@title"
        LAST_CLUB_URL = "//span[contains(text(),'Last club:')]//span//a//@href"
        MOST_GAMES_FOR_CLUB_NAME = "//span[contains(text(),'Most games for:')]//span//a//text()"
        RETIRED_SINCE_DATE = "//span[contains(text(),'Retired since:')]//span//text()"
        CURRENT_CLUB_CONTRACT_EXPIRES = "//span[text()='Contract expires: ']//span//text()"
        CURRENT_CLUB_CONTRACT_OPTION = "//span[contains(text(),'Contract option:')]//following::span[1]//text()"
        NAME_IN_HOME_COUNTRY = "//span[text()='Name in home country:']//following::span[1]//text()"
        FULL_NAME = "//span[text()='Full name:']//following::span[1]//text()"
        DATE_OF_BIRTH = "//span[text()='Date of birth:']//following::span[1]//a//text()"
        PLACE_OF_BIRTH_CITY = "//span[text()='Place of birth:']//following::span[1]//span//text()"
        PLACE_OF_BIRTH_COUNTRY = "//span[text()='Place of birth:']//following::span[1]//span//img//@title"
        AGE = "//span[text()='Age:']//following::span[1]//text()"
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
        SOCIAL_MEDIA = "//div[@class='socialmedia-icons']//@href"

    class Search:
        BASE = "//div[@class='box'][h2[contains(text(), 'players')]]"
        FOUND = "//text()"
        URL = BASE + "//td[@class='hauptlink']//a//@href"
        NAME = BASE + "//td[@class='hauptlink']//a//@title"
        POSITION = BASE + "//td[@class='zentriert'][1]//text()"
        CLUB_IMAGE = BASE + "//td[@class='zentriert'][2]//img//@src"
        CLUB_NAME = BASE + "//img[@class='tiny_wappen']//@title"
        AGE = BASE + "//td[@class='zentriert'][3]//text()"
        NATIONALITY = BASE + "//img//@title"
        MARKET_VALUE = BASE + "//td[@class='rechts hauptlink']//text()"

    class MarketValue:
        URL = "//a[@class='data-header__market-value-wrapper']//@href"
        CURRENT = (
            "//a[@class='data-header__market-value-wrapper']//text()[not(parent::p/@class='data-header__last-update')]"
        )
        HIGHCHARTS = "//script[@type='text/javascript'][text()[contains(.,'Highcharts.Chart')]]//text()"
        RANKINGS_NAMES = "//h3[@class='quick-fact__headline']//text()"
        RANKINGS_POSITIONS = "//span[contains(@class, 'quick-fact__content--large')]//text()"

    class Transfers:
        TRANSFERS_URLS = "//a[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__link']//@href"
        SEASONS = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__season']//text()"
        DATES = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__date']//text()"
        OLD_CLUBS_URLS = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__old-club']"
            "/a[@class='tm-player-transfer-history-grid__club-link']/@href"
        )
        OLD_CLUBS_NAMES = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__old-club']"
            "/a[@class='tm-player-transfer-history-grid__club-link']/text()"
        )
        NEW_CLUBS_URLS = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__new-club']"
            "/a[@class='tm-player-transfer-history-grid__club-link']/@href"
        )
        NEW_CLUBS_NAMES = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__new-club']"
            "/a[@class='tm-player-transfer-history-grid__club-link']/text()"
        )
        MARKET_VALUES = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__market-value']//text()"
        )
        FEES = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__fee']//text()"
        YOUTH_CLUBS = "//div[@data-viewport='Jugendvereine']//div//text()"

    class Stats:
        ROWS = "//table[@class='items']//tbody//tr"
        HEADERS = "//table[@class='items']//thead//tr//@title"
        COMPETITIONS_URLS = "//table[@class='items']//td[@class='hauptlink no-border-links']//a//@href"
        CLUBS_URLS = "//table[@class='items']//td[@class='hauptlink no-border-rechts zentriert']//a//@href"
        DATA = ".//text()"


class Clubs:
    class Profile:
        URL = "//div[@class='datenfakten-wappen']//@href"
        NAME = "//header//h1//text()"
        NAME_OFFICIAL = "//th[text()='Official club name:']//following::td[1]//text()"
        IMAGE = "//div[@class='datenfakten-wappen']//@src"
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
        BASE = "//div[@class='box'][h2[contains(text(), 'Clubs')]]"
        NAMES = BASE + "//td[@class='hauptlink']//a//@title"
        URLS = BASE + "//td[@class='hauptlink']//a//@href"
        COUNTRIES = BASE + "//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        MARKET_VALUES = BASE + "//td[@class='rechts']//text()"
        SQUADS = BASE + "//td[@class='zentriert']//text()"

    class Players:
        PAST_FLAG = "//div[@id='yw1']//thead//text()"
        CLUB_NAME = "//header//h1//text()"
        CLUB_URL = "//li[@id='overview']//@href"
        PAGE_NATIONALITIES = "//td[img[@class='flaggenrahmen']]"
        PAGE_INFOS = "//td[@class='posrela']"
        NAMES = "//td[@class='posrela']//a//text()"
        URLS = "//td[@class='hauptlink']//@href"
        POSITIONS = "//td[@class='posrela']//tr[2]//text()"
        DOB_AGE = "//div[@id='yw1']//td[3]//text()"
        NATIONALITIES = ".//img//@title"
        JOINED = ".//span/node()/@title"
        SIGNED_FROM = ".//a//img//@title"
        MARKET_VALUES = "//td[@class='rechts hauptlink']//text()"
        STATUSES = ".//td[@class='hauptlink']//span//@title"

        class Present:
            PAGE_SIGNED_FROM = "//div[@id='yw1']//td[8]"
            HEIGHTS = "//div[@id='yw1']//td[5]//text()"
            FOOTS = "//div[@id='yw1']//td[6]//text()"
            JOINED_ON = "//div[@id='yw1']//td[7]//text()"
            CONTRACTS = "//div[@id='yw1']//td[9]//text()"

        class Past:
            PAGE_SIGNED_FROM = "//div[@id='yw1']//td[9]"
            CURRENT_CLUB = "//div[@id='yw1']//td[5]//img//@title"
            HEIGHTS = "//div[@id='yw1']//td[6]/text()"
            FOOTS = "//div[@id='yw1']//td[7]//text()"
            JOINED_ON = "//div[@id='yw1']//td[8]//text()"
            CONTRACTS = "//div[@id='yw1']//td[10]//text()"


class Competitions:
    class Profile:
        URL = "//li[@id='overview']//@href"
        NAME = "//div[@class='data-header__headline-container']//h1//text()"

    class Search:
        BASE = "//div[@class='box'][h2[contains(text(), 'competitions')]]"
        URLS = BASE + "//td//a//@href"
        NAMES = BASE + "//td//a//@title"
        COUNTRIES = BASE + "//td[@class='zentriert'][1]//@title"
        CLUBS = BASE + "//td[@class='zentriert'][2]//text()"
        PLAYERS = BASE + "//td[@class='rechts']//text()"
        TOTAL_MARKET_VALUES = BASE + "//td[@class='zentriert'][3]//text()"
        MEAN_MARKET_VALUES = BASE + "//td[@class='zentriert'][4]//text()"
        CONTINENTS = BASE + "//td[@class='zentriert'][5]//text()"

    class Clubs:
        URLS = "//td[@class='hauptlink no-border-links']//a[1]//@href"
        NAMES = "//td[@class='hauptlink no-border-links']//a//text()"


class Commons:
    class Search:
        PAGE_NUMBER_LAST = "//li[@class='tm-pagination__list-item tm-pagination__list-item--icon-last-page']//@href"
        PAGE_NUMBER_ACTIVE = "//li[@class='tm-pagination__list-item tm-pagination__list-item--active']//@href"
