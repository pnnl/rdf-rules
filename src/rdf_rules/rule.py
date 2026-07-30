from beartype.vale import Is
from typing import Annotated
from pathlib import Path
from plum import dispatch


#from collections.abc import Callable # can't use callable return sigs with dispatch

class Maker:
    # dispatch does not work with beartype_this_package 
    # https://github.com/beartype/plum/issues/291
    # but this class is a workaround
    def __call__(self, *p , **kw):
        return self.make(*p, **kw)

    
    import pandas as pd
    from .data import table as tr
    @dispatch
    def make(self, path: Annotated[Path, Is[lambda p: p.suffix == '.csv'] ], **options) -> tr.CSVReader:
        return self.tr.CSVReader(path, **options)
    @dispatch
    def make(self, df: pd.DataFrame, **options) -> tr.Table:
        return self.tr.Table(df, **options)

    from .data import json as jr
    @dispatch
    def make(self, path: Annotated[Path, Is[lambda p: p.suffix in {'.json', '.geojson'}] ], **options) -> jr.JsonReader:
        return self.jr.JsonReader(path, **options)
    @dispatch
    def make(self, json: dict, **options) -> jr.JSON:
        return self.jr.JSON(json, **options)


make = Maker()
