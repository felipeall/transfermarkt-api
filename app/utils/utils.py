import re
from typing import Optional, Union


def zip_lists_into_dict(list_keys: list, list_values: list) -> dict:
    """
    Create a dictionary by pairing elements from two lists.

    Args:
        list_keys (list): List of keys.
        list_values (list): List of values.

    Returns:
        dict: A dictionary created by pairing elements from the input lists.
    """
    return {k: v for k, v in zip(list_keys, list_values)}


def extract_from_url(tfmkt_url: Optional[str], element: str = "id") -> Optional[str]:
    """
    Extract a specific element from a Transfermarkt URL using regular expressions.

    Args:
        tfmkt_url (str): The Transfermarkt URL from which to extract the element.
        element (str, optional): The element to extract (e.g., 'id', 'season_id', 'transfer_id').

    Returns:
        Optional[str]: The extracted element value or None if not found.
    """
    if not tfmkt_url:
        return None

    regex: str = (
        r"/(?P<code>[\w%-]+)"
        r"/(?P<category>[\w-]+)"
        r"/(?P<type>[\w-]+)"
        r"/(?P<id>\w+)"
        r"(/saison_id/(?P<season_id>\d{4}))?"
        r"(/transfer_id/(?P<transfer_id>\d+))?"
    )

    try:
        groups: dict = re.match(regex, trim(tfmkt_url)).groupdict()
    except TypeError:
        return None
    return groups.get(element)


def trim(text: Union[list, str]) -> str:
    """
    Trim and clean up text by removing leading and trailing whitespace and special characters.

    Args:
        text (Union[list, str]): The text or list of text to be trimmed.

    Returns:
        str: The trimmed and cleaned text.
    """
    if isinstance(text, list):
        text = "".join(text)

    return text.strip().replace("\xa0", "")


def safe_regex(text: Optional[Union[str, list]], regex, group: str) -> Optional[str]:
    """
    Safely apply a regular expression and extract a specific group from the matched text.

    Args:
        text (Optional[str]): The text to apply the regular expression to.
        regex: The regular expression pattern.
        group (str): The name of the group to extract.

    Returns:
        Optional[str]: The extracted group value or None if not found or if the input is not a string.
    """
    if not isinstance(text, (str, list)) or not text:
        return None

    try:
        groups = re.search(regex, trim(text)).groupdict()
        return groups.get(group)
    except AttributeError:
        return None


def remove_str(text: Optional[str], strings_to_remove: Union[str, list]) -> Optional[str]:
    """
    Remove specified strings from a text and return the cleaned text.

    Args:
        text (Optional[str]): The text to remove strings from.
        strings_to_remove (Union[str, list]): A string or list of strings to remove.

    Returns:
        Optional[str]: The cleaned text with specified strings removed or None if not found or if
            the input is not a string.
    """
    if not isinstance(text, str):
        return None

    strings_to_remove = list(strings_to_remove)

    for string in strings_to_remove:
        text = text.replace(string, "")

    return trim(text)


def safe_split(text: Optional[str], delimiter: str) -> Optional[list]:
    """
    Split a text using a delimiter and return a list of cleaned, trimmed values.

    Args:
        text (Optional[str]): The text to split.
        delimiter (str): The delimiter used for splitting.

    Returns:
        Optional[list]: A list of split and cleaned values or None if the input is not a string.
    """
    if not isinstance(text, str):
        return None

    return [trim(t) for t in text.split(delimiter)]


def to_camel_case(headers: list) -> list:
    """
    Convert a list of headers to camelCase format.

    Args:
        headers (list): A list of headers in snake_case or space-separated format.

    Returns:
        list: A list of headers in camelCase format.
    """
    camel_case_headers = ["".join(word.capitalize() for word in header.split()) for header in headers]
    camel_case_headers = [header[0].lower() + header[1:] for header in camel_case_headers]

    return [header for header in camel_case_headers]
