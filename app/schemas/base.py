import re
from datetime import date, datetime
from typing import Any, Optional

from dateutil import parser
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


class AuditMixin(BaseModel):
    updated_at: datetime = Field(default_factory=datetime.now)


class TransfermarktBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

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
    @classmethod
    def parse_str_to_date(
        cls,
        value: Any,
    ) -> Optional[date]:
        if value is None or value == "":
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        try:
            return parser.parse(str(value)).date()
        except (parser.ParserError, TypeError, ValueError):
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
    @classmethod
    def parse_str_to_int(
        cls,
        value: Any,
    ) -> Optional[int]:
        if value is None or value == "":
            return None

        # The new Transfermarkt JSON API returns actual numeric values.
        if isinstance(value, bool):
            return int(value)

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        value_string = str(value).strip()

        if not any(char.isdigit() for char in value_string):
            return None

        # Clean up HTML containing a market value.
        if "<" in value_string:
            matches = re.findall(
                r"€([\d,.]+(?:bn|[kmb])?)",
                value_string.lower(),
            )

            if not matches:
                return None

            value_string = matches[0]
        else:
            value_string = (
                value_string.lower()
                .replace("€", "")
                .replace("+", "")
                .replace("'", "")
                .replace(" ", "")
                .strip()
            )

        multiplier = 1

        if value_string.endswith("bn"):
            multiplier = 1_000_000_000
            value_string = value_string[:-2]
        elif value_string.endswith("k"):
            multiplier = 1_000
            value_string = value_string[:-1]
        elif value_string.endswith("m"):
            multiplier = 1_000_000
            value_string = value_string[:-1]
        elif value_string.endswith("b"):
            multiplier = 1_000_000_000
            value_string = value_string[:-1]

        # Transfermarkt may use either comma or dot as a decimal
        # separator depending on the domain.
        if "," in value_string and "." not in value_string:
            comma_parts = value_string.split(",")

            if (
                multiplier > 1
                and len(comma_parts) == 2
                and len(comma_parts[1]) <= 2
            ):
                value_string = value_string.replace(",", ".")
            else:
                value_string = value_string.replace(",", "")
        else:
            value_string = value_string.replace(",", "")

        try:
            return int(float(value_string) * multiplier)
        except (TypeError, ValueError):
            return None

    @field_validator(
        "height",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def parse_height(
        cls,
        value: Any,
    ) -> Optional[int]:
        if value is None or value == "":
            return None

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            # Handle values such as 1.75 metres.
            if 0 < value < 3:
                return int(round(value * 100))

            return int(value)

        value_string = str(value).strip()

        if not any(char.isdigit() for char in value_string):
            return None

        cleaned = (
            value_string.lower()
            .replace("m", "")
            .replace(" ", "")
            .replace("،", "")
        )

        # Existing HTML values commonly look like "1,75 m".
        if "," in cleaned and "." not in cleaned:
            parts = cleaned.split(",")

            if (
                len(parts) == 2
                and len(parts[0]) == 1
                and len(parts[1]) == 2
            ):
                cleaned = "".join(parts)
            else:
                cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(".", "")

        try:
            return int(cleaned)
        except ValueError:
            return None

    @field_validator(
        "days",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def parse_days(
        cls,
        value: Any,
    ) -> Optional[int]:
        if value is None or value == "":
            return None

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        days = "".join(
            filter(
                str.isdigit,
                str(value),
            )
        )

        return int(days) if days else None