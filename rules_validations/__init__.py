from dataclasses import dataclass
from typing import TypeVar, Callable, Any

from jinja2 import Environment, DebugUndefined

T = TypeVar('T')

env = Environment(undefined=DebugUndefined)


@dataclass
class ErrorWrapper(BaseException):
    key: str
    exception: Exception


ValidationError = BaseExceptionGroup


class Validator:
    _rules: dict = {}

    def add(self, path: str, statement: Callable[[T], Any] | str, message: str):
        if not callable(statement) and type(statement) != str:
            raise ValueError("statement must be a callable or a str")

        def assertion(values: T):
            try:
                if callable(statement):
                    statement_values = statement(values)
                else:
                    statement_values = env.from_string(statement).render(values=values.dict())
            except Exception as exc:
                return ErrorWrapper(path, exc)
            if statement_values:
                exc_msg = env.from_string(message).render(values=values.dict(), results=statement_values)
                return ErrorWrapper(path, AssertionError(exc_msg))

        try:
            self._rules[path].append(assertion)
        except KeyError:
            self._rules[path] = [assertion]

    def __call__(self, values: T, **kwargs):
        validation_errors: list[ErrorWrapper] = []
        for item, validators in self._rules.items():
            for validator in validators:
                if exc := validator(values):
                    validation_errors.append(exc)
        if validation_errors:
            raise ValidationError('', validation_errors)

    def add_json(self, json_data: dict):
        for path, rule in json_data.items():
            self.add(path, rule['test'], rule['msg'])

    @classmethod
    def from_json(cls, json_data: dict):
        new_instance = cls()
        new_instance.add_json(json_data)
        return new_instance
