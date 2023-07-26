import json
from typing import TypeVar, Callable, Any, IO

from jinja2 import Environment, DebugUndefined

from rules_validations.models.errors import ErrorWrapper, ValidationError
from rules_validations.models.rules import Rule

T = TypeVar('T')

env = Environment(undefined=DebugUndefined)


class Validator:
    _rules: dict = {}

    def add(self, path: str, statement: Callable[[T], Any], message: str):
        def assertion(values: T):
            try:
                statement_values = statement(values)
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

    @classmethod
    def from_dict(cls, rules: list[Rule]):
        new_instance = cls()
        for rule in rules:
            if rule["active"]:
                new_instance.add(
                    rule["path"],
                    rule['test'],
                    rule['msg']
                )
        return new_instance

    @classmethod
    def from_json_string(cls, json_str: str):
        return cls.from_dict([{
            "active": rule['active'],
            "path": rule['path'],
            "test": lambda values: env.from_string(rule['test']).render(values=values.dict()) == 'True',
            "msg": read_file_msg(rule['msg']),
        } for rule in json.loads(json_str)])

    @classmethod
    def from_json_file(cls, json_file: IO):
        return cls.from_json_string(json_file.read())


def read_file_msg(msg: str | dict) -> str:
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        if msg["type"] == 'template':
            return msg['value']
        if msg["type"] == 'file':
            with open(msg['value']) as f:
                return f.read()
    raise ValueError("msg not valid")
