"""Country reference data assembly shared by SDK and server."""

from transfermarkt_api.exceptions import UpstreamError
from transfermarkt_api.tfmkt import TfmktClient


async def list_countries(tfmkt: TfmktClient) -> dict:
    """List upstream country metadata, including historical entries."""
    countries = (await tfmkt.attributes()).get("countries")
    if not isinstance(countries, list) or not all(isinstance(country, dict) for country in countries):
        raise UpstreamError("Unexpected upstream payload for /attributes countries")
    return {"countries": countries}
