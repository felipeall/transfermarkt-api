import re
from typing import Optional, Union
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from lxml import etree
from requests import Response, TooManyRedirects


def make_request(url: str) -> Response:
    try:
        response: Response = requests.get(
            url=url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/113.0.0.0 "
                    "Safari/537.36"
                ),
            },
        )
    except TooManyRedirects:
        raise HTTPException(status_code=404, detail=f"Not found for url: {url}")
    if 400 <= response.status_code < 500:
        raise HTTPException(status_code=response.status_code, detail=f"Client Error. {response.reason} for url: {url}")
    elif 500 <= response.status_code < 600:
        raise HTTPException(status_code=response.status_code, detail=f"Server Error. {response.reason} for url: {url}")
    return response


def request_url_bsoup(url: str) -> BeautifulSoup:
    response: Response = make_request(url=url)
    return BeautifulSoup(markup=response.content, features="html.parser")


def convert_bsoup_to_page(bsoup: BeautifulSoup) -> ElementTree:
    return etree.HTML(str(bsoup))


def request_url_page(url: str) -> ElementTree:
    bsoup: BeautifulSoup = request_url_bsoup(url=url)
    return convert_bsoup_to_page(bsoup=bsoup)


def clean_response(nested: Union[dict, list]) -> Union[dict, list]:
    if isinstance(nested, dict):
        return {k: v for k, v in ((k, clean_response(v)) for k, v in nested.items()) if v or isinstance(v, bool)}
    if isinstance(nested, list):
        return [v for v in map(clean_response, nested) if v or isinstance(v, bool)]
    return nested


def zip_lists_into_dict(list_keys: list, list_values: list) -> dict:
    return {k: v for k, v in zip(list_keys, list_values)}


def extract_from_url(tfmkt_url: str, element: str = "id") -> Optional[str]:
    regex: str = (
        r"/(?P<code>[\w-]+)"
        r"/(?P<category>[\w-]+)"
        r"/(?P<type>[\w-]+)"
        r"/(?P<id>\w+)"
        r"(/saison_id/(?P<season_id>\d{4}))?"
        r"(/transfer_id/(?P<transfer_id>\d+))?"
    )
    try:
        groups: dict = re.match(regex, tfmkt_url).groupdict()
    except TypeError:
        return None
    return groups.get(element)


def trim(text: Union[list, str]) -> str:
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")


def get_list_by_xpath(self, xpath: str, remove_empty: Optional[bool] = True) -> Optional[list]:
    elements: list = self.page.xpath(xpath)
    if remove_empty:
        elements_valid: list = [trim(e) for e in elements if trim(e)]
    else:
        elements_valid: list = [trim(e) for e in elements]
    return elements_valid or []


def get_text_by_xpath(
    self,
    xpath: str,
    pos: int = 0,
    iloc: Optional[int] = None,
    iloc_from: Optional[int] = None,
    iloc_to: Optional[int] = None,
    join_str: Optional[str] = None,
) -> Optional[str]:
    try:
        element = self.page.xpath(xpath)
    except AttributeError:
        element = self.xpath(xpath)

    if not element:
        return None

    if isinstance(element, list):
        element = [trim(e) for e in element if trim(e)]

    if isinstance(iloc, int):
        element = element[iloc]

    if isinstance(iloc_from, int) and isinstance(iloc_to, int):
        element = element[iloc_from:iloc_to]

    if isinstance(iloc_to, int):
        element = element[:iloc_to]

    if isinstance(iloc_from, int):
        element = element[iloc_from:]

    if isinstance(join_str, str):
        return join_str.join([trim(e) for e in element])

    try:
        return trim(element[pos])
    except IndexError:
        return None


def safe_regex(text: Optional[str], regex, group: str) -> Optional[str]:
    if not isinstance(text, str):
        return None

    try:
        groups = re.search(regex, text).groupdict()
        return groups.get(group)
    except AttributeError:
        return None


def remove_str(text: Optional[str], strings_to_remove: Union[str, list]) -> Optional[str]:
    if not isinstance(text, str):
        return None

    strings_to_remove = list(strings_to_remove)

    for string in strings_to_remove:
        text = text.replace(string, "")

    return trim(text)


def safe_split(text: Optional[str], delimiter: str) -> Optional[list]:
    if not isinstance(text, str):
        return None

    return [trim(t) for t in text.split(delimiter)]
