from typing import Annotated

from fastapi import Depends, Request

from transfermarkt_api import Transfermarkt


def get_tfmkt(request: Request) -> Transfermarkt:
    """Return the shared upstream client created during server startup."""
    return request.app.state.tfmkt


Tfmkt = Annotated[Transfermarkt, Depends(get_tfmkt)]
