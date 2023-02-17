import re
from typing import Optional
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from lxml import etree
from requests import Response


def _make_request(url: str) -> Response:
    response: Response = requests.get(url=url, headers={"User-Agent": "Mozilla/5.0"})
    return response


def request_url_bsoup(url: str) -> BeautifulSoup:
    response: Response = _make_request(url=url)
    return BeautifulSoup(markup=response.content, features="html.parser")


def convert_bsoup_to_page(bsoup: BeautifulSoup) -> ElementTree:
    return etree.HTML(str(bsoup))


def request_url_page(url: str) -> ElementTree:
    bsoup: BeautifulSoup = request_url_bsoup(url=url)
    return convert_bsoup_to_page(bsoup=bsoup)


def clean_dict(dict_nested: dict) -> Optional[dict]:
    dict_clean: dict = {}
    for k, v in dict_nested.items():
        if isinstance(v, dict):
            v: dict = clean_dict(v)
        if v is not None:
            dict_clean[k] = v
    return dict_clean or None


def zip_lists_into_dict(list_keys: list, list_values: list) -> dict:
    return {k: v for k, v in zip(list_keys, list_values)}


def extract_from_url(tfmkt_url: str, element: str = "id") -> Optional[str]:
    regex: str = (
        r"/(?P<code>.+)"
        r"/(?P<category>\D+)"
        r"/(?P<type>\D+)"
        r"/(?P<id>\d+)"
        r"(/saison_id/(?P<season_id>\d{4}))?"
        r"(/transfer_id/(?P<transfer_id>\d+))?"
    )
    groups: dict = re.match(regex, tfmkt_url).groupdict()
    return groups.get(element)


def trim(text: str) -> str:
    return text.strip().replace("\xa0", "")


def get_list_by_xpath(self, xpath: str) -> Optional[list]:
    elements: list = self.page.xpath(xpath)
    elements_valid: list = [trim(e) for e in elements if trim(e)]
    return elements_valid or None


def get_text_by_xpath(self, xpath: str) -> Optional[str]:
    element: ElementTree = self.page.xpath(xpath)
    if element:
        return trim(element[0])
    else:
        return None
