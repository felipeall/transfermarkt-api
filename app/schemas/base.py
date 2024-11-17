from datetime import datetime

from dateutil import parser
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


class AuditMixin(BaseModel):
    updated_at: datetime = Field(default_factory=datetime.now)


class TransfermarktBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    @field_validator(
        "date_of_birth",
        "joined_on",
        "contract",
        "founded_on",
        "members_date",
        "from_date",
        "until_date",
        "date",
        "contract_expires",
        "joined",
        "retired_since",
        mode="before",
        check_fields=False,
    )
    def parse_str_to_date(cls, v: str):
        try:
            return parser.parse(v).date() if v else None
        except parser.ParserError:
            return None

    @field_validator(
        "current_market_value",
        "current_transfer_record",
        "market_value",
        "mean_market_value",
        "members",
        "total_market_value",
        "age",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
        "minutes_played",
        "fee",
        "appearances",
        "games_missed",
        mode="before",
        check_fields=False,
    )
    def parse_str_to_int(cls, v: str):
        parsed_value = (
            (
                v.replace("bn", "000000000")
                .replace("m", "000000")
                .replace("k", "000")
                .replace("€", "")
                .replace(".", "")
                .replace("+", "")
                .replace(".", "")
                .replace("'", "")
            )
            if v and any(char.isdigit() for char in v)
            else None
        )
        return int(parsed_value) if parsed_value else None

    @field_validator("height", mode="before", check_fields=False)
    def parse_height(cls, v: str):
        if not any(char.isdigit() for char in v):
            return None
        return int(v.replace(",", "").replace("m", ""))

    @field_validator("days", mode="before", check_fields=False)
    def parse_days(cls, v: str):
        days = "".join(filter(str.isdigit, v))
        return int(days) if days else None
