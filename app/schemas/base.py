from datetime import datetime
from pydantic.alias_generators import to_camel

from dateutil import parser
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TransfermarktBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    @field_validator("date_of_birth", "joined_on", "contract", "founded_on", "members_date", mode="before", check_fields=False)
    def parse_str_to_date(cls, v: str):
        return parser.parse(v).date()

    @field_validator("height", mode="before", check_fields=False)
    def parse_height(cls, v: str):
        return int(v.replace(",", "").replace("m", ""))

    @field_validator("market_value", "current_market_value", "current_transfer_record", "total_market_value", "mean_market_value", mode="before", check_fields=False)
    def parse_currency_value(cls, v: str):
        parsed_value = v.replace("bn", "000000000").replace("m", "000000").replace("k", "000").replace("€", "").replace(".", "").replace("+", "")
        return int(parsed_value) if parsed_value else None


class IDMixin(BaseModel):
    id: str


class AuditMixin(BaseModel):
    updated_at: datetime = Field(default_factory=datetime.now)
