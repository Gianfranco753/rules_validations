import json

from pydantic import BaseModel, ValidationError

from rules_validations import Validator
from rules_validations.baseEnum import BaseEnum

with open('test.json') as f:
    validator = Validator.from_json(json.load(f))
validator.add('val',
              lambda values: values.val != 1,
              "Valor distinto de 1")
validator.add('foo',
              lambda values: values.foo == 'Malo',
              "foo Malo")
validator.add('txt',
              "{% if values.txt == 'Malo' %}True{% endif %}",
              "txt Malo")


class Ident(BaseEnum):
    hola = 1
    chao = 2


class Noti(BaseModel):
    val: int
    foo: str
    bar: Ident
    txt: str


notis = (
    dict(val=1, foo='', bar=Ident.hola, txt='Hola'),
    dict(val=2, foo='Malo', bar='chao', txt='Hola'),
    dict(val=3, foo='Malo', bar='echao', txt='Hola'),
    dict(val=4, foo='Malo', bar='chao', txt='Malo'),
    dict(val=5, foo='', bar='chao', txt='Hola'),
)
for index, noti_data in enumerate(notis):
    try:
        noti = Noti(**noti_data)
    except ValidationError as excs:
        print(f"No se pudieron convertir los datos de la notificacion {index} por los siguientes errores:")
        for exc in excs.errors():
            print(f"\t - ({exc['loc']}, {exc['type']}('{exc['msg']}'))")
    else:
        try:
            validator(noti)
        except BaseExceptionGroup as excs:
            print(f"Se han detectado las siguientes alertas en la notificacion {index}:")
            for exc in excs.exceptions:
                print('\t -', exc.args)
        else:
            print(f"Notificacion {index} sin alertas")
