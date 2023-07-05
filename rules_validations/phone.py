from typing import Any, Callable, Generator

import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType
from pydantic.utils import update_not_none
from pydantic.validators import str_validator

__all__ = (
    "PhoneNumberFormat",
    "PhoneNumberType",
    "PhoneNumber",
)

GeneratorCallableStr = Generator[Callable[[str | int], str], None, None]


# https://github.com/samuelcolvin/pydantic/issues/1551
class PhoneNumber(str):
    region_code: str | None = 'CL'
    number_type: int | None = None
    format_type: int = PhoneNumberFormat.E164

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update(type="string", format="phoneNumber")
        update_not_none(
            field_schema,
            regionCode=cls.region_code,
            numberType=cls.number_type,
            formatType=cls.format_type,
        )

    @classmethod
    def __get_validators__(cls) -> GeneratorCallableStr:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, value: str | int) -> str:
        try:
            n = phonenumbers.parse(value, cls.region_code)
        except phonenumbers.NumberParseException as e:
            raise ValueError(e._msg)  # noqa

        if cls.region_code and not phonenumbers.is_valid_number_for_region(
            n, cls.region_code
        ):
            raise ValueError(
                f"Phone number is not valid for the region code '{cls.region_code}'"
            )
        if cls.number_type and phonenumbers.number_type(n) != cls.number_type:
            raise ValueError("Phone number type is invalid")

        return str(phonenumbers.format_number(n, cls.format_type))
