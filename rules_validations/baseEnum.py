from enum import IntEnum
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from rules_validations.normalize import normalize_value


class BaseEnum(IntEnum):
    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[Any], handler: GetCoreSchemaHandler) -> CoreSchema:
        schema = handler(source)
        return core_schema.no_info_before_validator_function(cls.validate, schema)

    @classmethod
    def validate(cls, value: str | int):
        if isinstance(value, cls):
            return value
        try:
            if isinstance(value, str):
                clean_value = normalize_value(value)
                try:
                    return cls[clean_value]
                except KeyError:
                    try:
                        return cls(clean_value)
                    except ValueError:
                        raise ValueError(f'{value} is not a valid {cls.__name__}')
            elif isinstance(value, int):
                return cls(value)
            else:
                raise ValueError(f'{value} is not a valid {cls.__name__}')
        except KeyError as e:
            raise ValueError(f'{e} is not a valid {cls.__name__}')

    def __new__(cls, value, *labels):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = tuple(normalize_value(label) for label in labels)
        return obj

    @classmethod
    def _missing_(cls, input_str):
        for finger in cls:
            if input_str in finger.label:
                return finger
        raise ValueError(f"{cls.__name__} has no value matching {input_str}")
