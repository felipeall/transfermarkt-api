from fastapi import APIRouter

from app.schemas.countries import Countries
from app.tfmkt import Tfmkt

router = APIRouter()


@router.get("/", response_model=Countries)
async def list_countries(tfmkt: Tfmkt) -> dict:
    """List country reference IDs, including historical entries, for use in country-filtered endpoints."""
    attributes = await tfmkt.attributes()
    return {"countries": attributes["countries"]}
