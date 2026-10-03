from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.tfmkt.freshness import data_fetched_at


class AuditMixin(BaseModel):
    updated_at: datetime = Field(
        default_factory=data_fetched_at,
        description="When the upstream data in this response was fetched (oldest fetch if served from cache).",
    )


class TransfermarktBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
