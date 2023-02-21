class Players(object):
    class Profile(object):
        ID: str = "//div[@data-action='profil']//@data-id"
        URL: str = "//a[@class='tm-subnav-item megamenu']//@href"
        NAME: str = "//h1[@class='data-header__headline-wrapper']//text()"
        IMAGE_URL: str = "//div[@id='fotoauswahlOeffnen']//img//@src"
        SHIRT_NUMBER: str = "//span[@class='data-header__shirt-number']//text()"
        CURRENT_CLUB_NAME: str = "//span[@class='data-header__club']//a//text()"
        CURRENT_CLUB_URL: str = "//span[@class='data-header__club']//a//@href"
        CURRENT_CLUB_JOINED: str = "//span[text()='Joined: ']//span//text()"
        CURRENT_CLUB_CONTRACT_EXPIRES: str = "//span[text()='Contract expires: ']//span//text()"
        CURRENT_CLUB_CONTRACT_OPTION: str = "//span[contains(text(),'Contract option:')]//following::span[1]//text()"
        NAME_IN_HOME_COUNTRY: str = "//span[text()='Name in home country:']//following::span[1]//text()"
        FULL_NAME: str = "//span[text()='Full name:']//following::span[1]//text()"
        DATE_OF_BIRTH: str = "//span[text()='Date of birth:']//following::span[1]//a//text()"
        PLACE_OF_BIRTH_CITY: str = "//span[text()='Place of birth:']//following::span[1]//span//text()"
        PLACE_OF_BIRTH_COUNTRY: str = "//span[text()='Place of birth:']//following::span[1]//span//img//@title"
        AGE: str = "//span[text()='Age:']//following::span[1]//text()"
        HEIGHT: str = "//span[text()='Height:']//following::span[1]//text()"
        CITIZENSHIP: str = "//span[text()='Citizenship:']//following::span[1]//text()"
        POSITION: str = "//span[text()='Position:']//following::span[1]//text()"
        POSITION_MAIN: str = "//dt[contains(text(),'Main position:')]//following::dd[1]//text()"
        POSITION_OTHER: str = "//dt[contains(text(),'Other position:')]//following::dd//text()"
        FOOT: str = "//span[text()='Foot:']//following::span[1]//text()"
        MARKET_VALUE_CURRENT: str = "//div[@class='tm-player-market-value-development__current-value']//text()"
        MARKET_VALUE_HIGHEST: str = "//div[@class='tm-player-market-value-development__max-value']//text()"
        AGENT_NAME: str = "//span[text()='Player agent:']//following::span[1]//a//text()"
        AGENT_URL: str = "//span[text()='Player agent:']//following::span[1]//a//@href"
        OUTFITTER: str = "//span[contains(text(),'Outfitter:')]//following::span[1]//text()"
        SOCIAL_MEDIA: str = "//div[@class='socialmedia-icons']//@href"

    class Search(object):
        RESULT: str = "//div[h2[contains(text(), 'players')]]"
        RESULT_NATIONALITIES: str = ".//td[img[@class='flaggenrahmen']]"
        RESULT_CLUBS: str = ".//td[@class='zentriert'][2]"
        NAMES: str = ".//td[@class='hauptlink']//a//@title"
        URLS: str = ".//td[@class='hauptlink']//a//@href"
        AGES: str = ".//td[@class='zentriert'][3]//text()"
        POSITIONS: str = ".//td[@class='zentriert'][1]//text()"
        CLUBS_URLS: str = ".//a//@href"
        CLUBS_NAMES: str = ".//img[@class='tiny_wappen']//@title"
        MARKET_VALUES: str = ".//td[@class='rechts hauptlink']//text()"
        NATIONALITIES: str = ".//img//@title"

    class MarketValue(object):
        URL: str = "//a[@class='data-header__market-value-wrapper']//@href"
        CURRENT_VALUE_AND_UPDATED: str = "//a[@class='data-header__market-value-wrapper']//text()"
        RANKINGS_NAMES: str = "//h3[@class='quick-fact__headline']//text()"
        RANKINGS_POSITIONS: str = "//span[contains(@class, 'quick-fact__content--large')]//text()"

    class Transfers(object):
        PLAYER_URL: str = "//li[@id='transfers']//a//@href"
        TRANSFERS_URLS: str = "//a[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__link']//@href"
        SEASONS: str = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__season']//text()"
        DATES: str = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__date']//text()"
        CLUBS_NAMES: str = "//*[@class='tm-player-transfer-history-grid__club-link']//text()"
        FEES: str = "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__fee']//text()"
        YOUTH_CLUBS: str = "//div[@data-viewport='Jugendvereine']//div//text()"
        FROM_CLUBS_URLS: str = (
            "//*[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__old-club']//a[1]//@href"
        )
        TO_CLUBS_URLS: str = (
            "//*[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__new-club']//a[1]//@href"
        )
        MARKET_VALUES: str = (
            "//div[@class='grid__cell grid__cell--center tm-player-transfer-history-grid__market-value']//text()"
        )


class Clubs(object):
    class Profile(object):
        URL: str = "//div[@class='datenfakten-wappen']//@href"
        NAME: str = "//header//h1//text()"
        NAME_OFFICIAL: str = "//th[text()='Official club name:']//following::td[1]//text()"
        IMAGE: str = "//div[@class='datenfakten-wappen']//@src"
        LEGAL_FORM: str = "//th[text()='Legal form:']//following::td[1]//text()"
        ADDRESS_LINE_1: str = "//th[text()='Address:']//following::td[1]//text()"
        ADDRESS_LINE_2: str = "//th[text()='Address:']//following::td[2]//text()"
        ADDRESS_LINE_3: str = "//th[text()='Address:']//following::td[3]//text()"
        TEL: str = "//th[text()='Tel:']//following::td[1]//text()"
        FAX: str = "//th[text()='Fax:']//following::td[1]//text()"
        WEBSITE: str = "//th[text()='Website:']//following::td[1]//text()"
        FOUNDED_ON: str = "//th[text()='Founded:']//following::td[1]//text()"
        MEMBERS: str = "//th[text()='Members:']//following::td[1]//text()"
        MEMBERS_DATE: str = "//th[text()='Members:']//following::td[1]//text()"
        OTHER_SPORTS: str = "//th[text()='Other sports:']//following::td[1]//text()"
        COLORS: str = "//p[@class='vereinsfarbe']//@style"
        STADIUM_NAME: str = "//li[contains(text(), 'Stadium:')]//span//a//text()"
        STADIUM_SEATS: str = "//li[contains(text(), 'Stadium:')]//span//span//text()"
        TRANSFER_RECORD: str = "//li[contains(text(), 'Current transfer record:')]//a//text()"
        MARKET_VALUE: str = "//a[@class='data-header__market-value-wrapper']//text()"
        CONFEDERATION: str = "//li[contains(text(), 'Konföderation:')]//span//text()"
        RANKING: str = "//li[contains(text(), 'FIFA World Ranking:')]//span//a//text()"
        SQUAD_SIZE: str = "//li[contains(text(), 'Squad size:')]//span//text()"
        SQUAD_AVG_AGE: str = "//li[contains(text(), 'Average age:')]//span//text()"
        SQUAD_FOREIGNERS: str = "//li[contains(text(), 'Foreigners:')]//span[1]//a//text()"
        SQUAD_NATIONAL_PLAYERS: str = "//li[contains(text(), 'National team players:')]//span//a//text()"
        LEAGUE_ID: str = "//span[@itemprop='affiliation']//a//@href"
        LEAGUE_NAME: str = "//span[@itemprop='affiliation']//a//text()"
        LEAGUE_COUNTRY_ID: str = (
            "//div[@class='data-header__club-info']//img[contains(@class, 'flaggenrahmen')]//@data-src"
        )
        LEAGUE_COUNTRY_NAME: str = (
            "//div[@class='data-header__club-info']//img[contains(@class, 'flaggenrahmen')]//@title"
        )
        LEAGUE_TIER: str = "//div[@class='data-header__club-info']//strong//text()//following::span[1]/a/text()[2]"
        CRESTS_HISTORICAL: str = "//div[@class='wappen-datenfakten-wappen']//@src"

    class Search(object):
        RESULT: str = "//div[h2[contains(text(), 'Clubs')]]"
        NAMES: str = ".//td[@class='hauptlink']//a//@title"
        URLS: str = ".//td[@class='hauptlink']//a//@href"
        COUNTRIES: str = ".//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        MARKET_VALUES: str = ".//td[@class='rechts']//text()"
        SQUADS: str = ".//td[@class='zentriert']//text()"

    class Players(object):
        CLUB_NAME: str = "//header//h1//text()"
        CLUB_URL: str = "//li[@id='overview']//@href"
        PAGE_NATIONALITIES: str = "//td[img[@class='flaggenrahmen']]"
        PAGE_INFOS: str = "//td[@class='posrela']"
        NAMES: str = "//td[@class='posrela']//a//text()"
        URLS: str = "//td[@class='hauptlink']//@href"
        POSITIONS: str = "//td[@class='posrela']//tr[2]//text()"
        AGES: str = "//div[@id='yw1']//td[3]//text()"
        NATIONALITIES: str = ".//img//@title"
        MARKET_VALUES: str = "//td[@class='rechts hauptlink']//text()"
        JOINED: str = ".//span/node()/@title"
        STATUSES: str = ".//td[@class='hauptlink']//span//@title"


class Competitions(object):
    class Profile(object):
        URL: str = "//li[@id='overview']//@href"
        NAME: str = "//div[@class='data-header__headline-container']//h1//text()"

    class Clubs(object):
        URLS: str = "//td[@class='hauptlink no-border-links']//a[1]//@href"
        NAMES: str = "//td[@class='hauptlink no-border-links']//a//text()"
