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
    class Search(object):
        RESULT: str = "//div[h2[contains(text(), 'Clubs')]]"
        NAMES: str = ".//td[@class='hauptlink']//a//@title"
        URLS: str = ".//td[@class='hauptlink']//a//@href"
        COUNTRIES: str = ".//td[@class='zentriert']//img[@class='flaggenrahmen']//@title"
        MARKET_VALUES: str = ".//td[@class='rechts']//text()"
        SQUADS: str = ".//td[@class='zentriert']//text()"
