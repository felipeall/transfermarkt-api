class Players(object):
    class Header(object):
        PLAYER_NAME: str = "//h1[@class='data-header__headline-wrapper']//text()"
        PLAYER_IMAGE_URL: str = "//div[@id='fotoauswahlOeffnen']//img//@src"
        SHIRT_NUMBER: str = "//span[@class='data-header__shirt-number']//text()"
        CURRENT_CLUB_NAME: str = "//span[@class='data-header__club']//a//text()"
        CURRENT_CLUB_URL: str = "//span[@class='data-header__club']//a//@href"
        CURRENT_CLUB_JOINED: str = "//span[text()='Joined: ']//span//text()"
        CURRENT_CLUB_CONTRACT_EXPIRES: str = "//span[text()='Contract expires: ']//span//text()"
        CURRENT_CLUB_CONTRACT_OPTION: str = "//span[contains(text(),'Contract option:')]//following::span[1]//text()"

    class Profile(object):
        PLAYER_ID: str = "//div[@data-action='profil']//@data-id"
        PLAYER_URL: str = "//a[@class='tm-subnav-item megamenu']//@href"

    class Data(object):
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
        PLAYER_AGENT_NAME: str = "//span[text()='Player agent:']//following::span[1]//a//text()"
        PLAYER_AGENT_URL: str = "//span[text()='Player agent:']//following::span[1]//a//@href"
        CURRENT_CLUB_NAME: str = "//span[contains(text(),'Current club:')]//following::span[1]//a[2]//text()"
        CURRENT_CLUB_URL: str = "//span[contains(text(),'Current club:')]//following::span[1]//a[2]//@href"
        OUTFITTER: str = "//span[contains(text(),'Outfitter:')]//following::span[1]//text()"
        SOCIAL_MEDIA: str = "//div[@class='socialmedia-icons']//@href"


class Search(object):
    class Players(object):
        RESULT_PLAYERS: str = "//div[h2[contains(text(), 'players')]]"
        RESULT_NATIONALITIES: str = ".//td[img[@class='flaggenrahmen']]"
        PLAYERS_NAMES: str = ".//td[@class='hauptlink']//a//@title"
        PLAYERS_URLS: str = ".//td[@class='hauptlink']//a//@href"
        PLAYERS_CLUB: str = ".//img[@class='tiny_wappen']//@title"
        PLAYERS_MARKET_VALUES: str = ".//td[@class='rechts hauptlink']//text()"
        PLAYERS_NATIONALITIES: str = ".//img//@title"


class MarketValue(object):
    class Players(object):
        MARKET_VALUE_URL: str = "//a[@class='data-header__market-value-wrapper']//@href"
        CURRENT_VALUE_AND_UPDATED: str = "//a[@class='data-header__market-value-wrapper']//text()"
        RANKINGS_NAMES: str = "//h3[@class='quick-fact__headline']//text()"
        RANKINGS_POSITIONS: str = "//span[contains(@class, 'quick-fact__content--large')]//text()"
