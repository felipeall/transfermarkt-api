from typing import Annotated

from fastapi import Depends, Request

from transfermarkt_api.tfmkt import TfmktClient


def get_tfmkt(request: Request) -> TfmktClient:
    """Return the shared upstream client created during server startup."""
    return request.app.state.tfmkt


Tfmkt = Annotated[TfmktClient, Depends(get_tfmkt)]
