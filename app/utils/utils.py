import re
from typing import Optional, Union


def clean_response(response: Union[dict, list]) -> Union[dict, list]:
    if isinstance(response, dict):
        return {
            k: v
            for k, v in ((k, clean_response(v)) for k, v in response.items())
            if (v or isinstance(v, bool)) and v != "-" and v != "N/A" and v != "m"
        }
    if isinstance(response, list):
        return [v for v in map(clean_response, response) if (v or isinstance(v, bool)) and v != "-"]
    return response


def zip_lists_into_dict(list_keys: list, list_values: list) -> dict:
    return {k: v for k, v in zip(list_keys, list_values)}


def extract_from_url(tfmkt_url: str, element: str = "id") -> Optional[str]:
    regex: str = (
        r"/(?P<code>[\w%-]+)"
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


def to_camel_case(headers: list) -> list:
    camel_case_headers = ["".join(word.capitalize() for word in header.split()) for header in headers]
    camel_case_headers = [header[0].lower() + header[1:] for header in camel_case_headers]

    return [header.replace("Id", "ID") for header in camel_case_headers]
