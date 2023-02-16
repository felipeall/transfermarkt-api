from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from lxml import etree
from requests import Response


def _make_request(url: str) -> Response:
    response: Response = requests.get(url=url, headers={"User-Agent": "Mozilla/5.0"})

    return response


def request_url_page(url: str) -> ElementTree:
    response: Response = _make_request(url=url)
    bsoup: BeautifulSoup = BeautifulSoup(markup=response.content, features="html.parser")
    tree: ElementTree = etree.HTML(str(bsoup))

    return tree


def clean_dict(dict_nested: dict) -> dict:
    dict_clean: dict = {}
    for k, v in dict_nested.items():
        if isinstance(v, dict):
            v: dict = clean_dict(v)
        if v is not None:
            dict_clean[k] = v
    return dict_clean or None
