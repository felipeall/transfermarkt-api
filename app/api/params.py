from typing import Annotated

from fastapi import Query

PageNumber = Annotated[int, Query(ge=1, description="1-based page number.")]
