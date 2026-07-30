from typing import Literal, Callable

from pathlib import Path

types = Literal['csv'] | Literal['parquet'] | Literal['excel']

from ..rule import BaseMeta
import pandas as pd
class Table(BaseMeta):
    from ..prefixes import prefixes
    def __init__(self, df: Callable[[], pd.DataFrame] | pd.DataFrame,
            name: str | None = None, *,
            data_prefix=prefixes['data'],
            data_id_prefix=prefixes['data.id'],
            json2rdf_options = {},
                 ) -> None:
        self._df = df
        self.name = name if name else str(id(df))
        self.data_prefix = data_prefix
        self.data_id_prefix = data_id_prefix
        self.json2rdf_options = json2rdf_options

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
        return {'name': self.name }
        

class CSVReader(BaseMeta):
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
        self.table = Table( pd.read_csv(path, **reading_args) ,
            data_prefix=data_prefix,
            data_id_prefix=data_id_prefix,
            json2rdf_options = json2rdf_options,
        )

    def params(self):
        _ = {'path': self.path.as_posix(), } # could do name but path is good enough 
        return _

    def data(self, db):
        _ = db
        return self.table.data(_)


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
    def make(self, path: Annotated[Path, Is[lambda p: p.suffix == '.csv'] ], **options) -> CSVReader:
        return CSVReader(path, **options)
    @dispatch
    def make(self, df: pd.DataFrame, **options) -> Table:
        return Table(df, **options)

    def __call__(self, *p , **kw):
        return self.make(*p, **kw)
make = Maker()
