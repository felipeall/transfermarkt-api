from typing import Annotated

from fastapi import Depends, Request

from app.tfmkt.client import TfmktClient as TfmktClient


def get_tfmkt(request: Request) -> TfmktClient:
    """FastAPI dependency returning the shared tfmkt client created in the app lifespan."""
    return request.app.state.tfmkt


Tfmkt = Annotated[TfmktClient, Depends(get_tfmkt)]
