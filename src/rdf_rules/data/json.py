from collections.abc import Callable
from pathlib import Path

from ..rule import BaseMeta
class JSON(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, json: Callable[[], str | dict] | str | dict,
            name: str | None = None, *,
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
                 ) -> None:
        self._json = json
        self.name = name if name else str(id(json))
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options


    #from functools import cache
    #@cache
    def json(self) -> str | dict:
        if callable(self._json):
            _ = self._json()
        else:
            _ = self._json
        return _

    def data(self, db):
        _ = db
        _ = self.json()
        from json2rdf import json2rdf as j2r
        _ = j2r(_,
                subject_id_keys = {}, # the id is the row number
                key_prefix = ('data', self.data_prefix),
                id_prefix= ('data.id',self.data_id_prefix ),
                **self.json2rdf_options)
        from pyoxigraph import parse, RdfFormat
        _ = parse(_ , format=RdfFormat.TURTLE)
        yield from _

    def params(self):
        return {'name': self.name }
        

class JsonReader(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, path: Path,
            reading_args: dict = {},
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
                 ) -> None:
        self.path = path
        self.reading_args = reading_args
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options
        from json import load
        self.json = JSON( lambda: load(open(path), **reading_args),
            data_prefix=data_prefix,
            data_id_prefix=data_id_prefix,
            json2rdf_options = json2rdf_options)

    def params(self):
        _ = {'path': self.path.as_posix(), } # could do name but path is good enough
        return _

    def data(self, db):
        _ = db
        return self.json.data(_)


### TODO: xl reader

class Maker:
    # dispatch does not work with beartype_this_package 
    # https://github.com/beartype/plum/issues/291
    # but this class is a workaround
    from beartype.vale import Is
    from typing import Annotated
    from pathlib import Path
    from plum import dispatch
    @dispatch
    def make(self, path: Annotated[Path, Is[lambda p: p.suffix in {'.json', '.geojson'}] ], **options) -> JsonReader:
        return JsonReader(path, **options)
    @dispatch
    def make(self, json: str | dict | Callable[[], str | dict], **options) -> JSON:
        return JSON(json, **options)

    def __call__(self, *p , **kw):
        return self.make(*p, **kw)
make = Maker()
