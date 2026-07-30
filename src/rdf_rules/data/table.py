from collections.abc import Callable
from pathlib import Path

    

import pandas as pd
from ..base import BaseMeta
class Table(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, df: Callable[[], pd.DataFrame] | pd.DataFrame,
            name: str | None = None, *,
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
            additional_params = {}
                 ) -> None:
        self._df = df
        self.name = name if name else str(id(df))
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options
        self.additional_params = additional_params

    #from functools import cache
    #@cache
    def df(self) -> pd.DataFrame:
        if callable(self._df):
            _ = self._df()
        else:
            _ = self._df
        _ = _.convert_dtypes()
        return _

    def data(self, db):
        _ = db
        _ = self.df()
        _ = _.to_json(orient='records')
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
        return {
            'name': self.name,
            **self.additional_params,
                 }
        

class CSVReader(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, path: Path,
            reading_args: dict = {},
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
            additional_params = {}
                 ) -> None:
        self.path = path
        self.reading_args = reading_args
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options
        self.additional_params = additional_params
        self.table = Table( lambda: pd.read_csv(path, **reading_args) ,
            data_prefix=data_prefix,
            data_id_prefix=data_id_prefix,
            json2rdf_options = json2rdf_options,
        )

    def params(self):
        _ = {
            'path': self.path.as_posix(),
            **self.additional_params
              } 
        return _

    def data(self, db):
        _ = db
        return self.table.data(_)

### TODO: xl reader


