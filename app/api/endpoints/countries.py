from fastapi import APIRouter

from app.api.dependencies import Tfmkt
from transfermarkt_api.schemas import Countries

router = APIRouter()


@router.get("/")
async def list_countries(tfmkt: Tfmkt) -> Countries:
    """List country reference metadata, including historical entries."""
    return await tfmkt.countries()
