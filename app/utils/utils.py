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


def request_url_bsoup(url: str) -> BeautifulSoup:
    response: Response = _make_request(url=url)
    bsoup: BeautifulSoup = BeautifulSoup(markup=response.content, features="html.parser")

    return bsoup


def clean_dict(dict_nested: dict) -> dict:
    dict_clean: dict = {}
    for k, v in dict_nested.items():
        if isinstance(v, dict):
            v: dict = clean_dict(v)
        if v is not None:
            dict_clean[k] = v
    return dict_clean or None


def zip_lists_into_dict(list_keys: list, list_values: list) -> dict:
    return {k: v for k, v in zip(list_keys, list_values)}


def extract_id_from_tfmkt_url(tfmkt_url: str):
    return tfmkt_url.split("/")[-1]


def trim(text: str):
    return text.strip().replace("\xa0", "")
