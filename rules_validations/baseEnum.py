from enum import IntEnum


def normalize_value(value) -> str:
    return value \
        .lower() \
        .replace('á', 'a').replace('ä', 'a') \
        .replace('é', 'e').replace('ë', 'e') \
        .replace('í', 'i').replace('ï', 'i') \
        .replace('ó', 'o').replace('ö', 'o') \
        .replace('ú', 'u').replace('ü', 'u') \
        .replace('(', '_') \
        .replace(')', '_') \
        .replace('/', '_') \
        .replace('+', 'p') \
        .replace(',', '_') \
        .replace('-', '_') \
        .replace(' ', '_')


class BaseEnum(IntEnum):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        print(1, value)
        try:
            if type(value) == str:
                clean_value = normalize_value(value)
                print(3, clean_value)
                try:
                    print(2, cls[clean_value])
                    return cls[clean_value]
                except KeyError:
                    print(4, cls(clean_value))
                    return cls(clean_value)

            elif type(value) == int:
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
