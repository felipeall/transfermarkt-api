from fastapi import APIRouter, HTTPException

from app.schemas.countries import Countries
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/", response_model=Countries)
async def list_countries(tfmkt: Tfmkt) -> dict:
    """List country reference IDs, including historical entries, for use in country-filtered endpoints."""
    countries = (await tfmkt.attributes()).get("countries")
    if not isinstance(countries, list) or not all(isinstance(country, dict) for country in countries):
        raise HTTPException(status_code=502, detail="Unexpected upstream payload for /attributes countries")
    return {"countries": countries}
