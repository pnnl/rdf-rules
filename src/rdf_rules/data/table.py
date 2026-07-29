from typing import Literal, Callable

from plum import dispatch
#from beartype import beartype
from pathlib import Path

types = Literal['csv'] | Literal['parquet'] | Literal['excel']

from ..rule import BaseMeta
import pandas as pd
#@beartype
class Table(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self,
            df: pd.DataFrame,
            name: str | None = None, *,
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
                 ) -> None:
        self.name = name if name else str(id(df))
        self.df = df
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options

    #from functools import cache
    #@cache
    #def 

    def data(self, db):
        _ = db
        _ = self.df
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
        return {'name': self.name }
        

class CSVReader:
    def __init__(self, source: Path | Callable,
                 reading_args: dict = {}, 
                 index_prefix = str,
                 data_prefix = str,
                 ) -> None:
        self.source = source
        self.reading_args = reading_args

    def params(self):
        _ = {'source': self.source, }
        return _

    @dispatch
    def json(self, src: Path):
        _ = pd.read_csv(src)
        _ = _.convert_dtypes()
        _ = _.to_json()
        return _
    @dispatch
    def json(self, src: Callable):
        _ = pd.read_csv(src())
        _ = _.to_json()
        return _


@dispatch
def df(path: Path):
    ...


@dispatch
def make(f: Callable[[], pd.DataFrame],):# type: types, reading_args: dict):
    df: pd.DataFrame = f()
    df = df.to_json()

    return 'df'
@dispatch
def xmake(f: Callable[[], str],):# type: types, reading_args: dict):
    return 's'

#csv , xl (table), parquet
