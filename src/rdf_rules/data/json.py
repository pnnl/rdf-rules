from collections.abc import Callable
from pathlib import Path


def validate(s, **kw):
    from json import loads
    try:
        loads(s, **kw)
        return True
    except:
        return False


from ..base import BaseMeta
class JSON(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, json: Callable[[], str | dict] | str | dict,
            name: str | None = None, *,
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
            additional_params = {},
                 ) -> None:
        self._json = json
        self.name = name if name else str(id(json))
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options
        self.additional_params = additional_params


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
        return {'name': self.name,
                **self.additional_params }
        

class JsonReader(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, path: Path,
            reading_args: dict = {},
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
            additional_params = {},
                 ) -> None:
        self.path = path
        self.reading_args = reading_args
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options
        self.additional_params = additional_params
        from json import load
        self.json = JSON( lambda: load(open(path), **reading_args),
            data_prefix=data_prefix,
            data_id_prefix=data_id_prefix,
            json2rdf_options = json2rdf_options)

    def params(self):
        _ = {'path': self.path.as_posix(),# could do name but path is good enough
             **self.additional_params,
              } 
        return _

    def data(self, db):
        _ = db
        return self.json.data(_)


