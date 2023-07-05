from typing import TypeVar, Callable, Generic, Any

from jinja2 import Environment, DebugUndefined
from pydantic.error_wrappers import ErrorWrapper, ValidationError

T = TypeVar('T')

env = Environment(undefined=DebugUndefined)


class Validators(Generic[T], dict[tuple[str, ...], list[Callable[[T], None]]]):
    def __init__(self, pydantic_model: type[T]):
        super().__init__()
        self.pydantic_model = pydantic_model

    def get_type(self) -> type[T]:
        return self.pydantic_model

    def add(self, path: tuple[str, ...] | str, statement: Callable[[T], Any], message: str):
        def assertion(values: T):
            statement_values = statement(values)
            if statement_values:
                raise AssertionError(env.from_string(message).render(values=values.dict(), results=statement_values))

        try:
            self[path].append(assertion)
        except KeyError:
            self[path] = [assertion]

    def __setitem__(self, key, value):
        key = key if type(key) is tuple else (key,)
        return super().__setitem__(key, value)

    def __getitem__(self, item):
        item = item if type(item) is tuple else (item,)
        return super().__getitem__(item)

    def __call__(self, pydantic_values: T | None = None, **kwargs):
        validation_errors: list[ErrorWrapper] = []
        # validate model
        if not isinstance(pydantic_values, self.pydantic_model):
            try:
                pydantic_values = self.pydantic_model(**kwargs)
            except ValidationError as exc:
                for error in exc.raw_errors:
                    validation_errors.append(error)
        # validate other functions
        for item in pydantic_values.dict().keys():
            try:
                for validator in self[item]:
                    try:
                        validator(pydantic_values)
                    except (ValidationError, ValueError, AssertionError) as e:
                        validation_errors.append(ErrorWrapper(e, (item,)))
                    except AttributeError:
                        pass  # print(e.name, e.obj, e.args)
            except KeyError:
                pass  # No existe una regla para este key
        if validation_errors:
            raise ValidationError(validation_errors, self.pydantic_model)
