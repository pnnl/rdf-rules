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
    def make(self, path: tr.paths.type.csv, **options) -> tr.CSVReader:
        return self.tr.CSVReader(path, **options)
    @dispatch
    def make(self, df: pd.DataFrame, **options) -> tr.Table:
        return self.tr.Table(df, **options)

    from .data import json as jr
    @dispatch
    def make(self, path: jr.path.type, **options) -> jr.JsonReader:
        return self.jr.JsonReader(path, **options)
    @dispatch
    def make(self, json: dict | jr.Str, **options) -> jr.JSON:
        return self.jr.JSON(json, **options)

    from .data import rdf as rr
    @dispatch
    def make(self, path: rr.paths.type.ttl, **options) -> rr.TTLReader:
        return self.rr.TTLReader(path, **options)
    @dispatch
    def make(self, ttl: rr.TTL.type.Str, **options) -> rr.TTL:
        return self.rr.TTL(ttl, **options)

    from . import construct as cr
    @dispatch
    def make(self, path: cr.path.type, **options) -> cr.ConstructQuery:
        return self.cr.ConstructQuery(path=path, **options)
    @dispatch
    def make(self, query: cr.Str, **options) -> cr.ConstructQuery:
        return self.cr.ConstructQuery(query=query, **options)

    from . import ontology as orr
    @dispatch
    def make(self, ontology: orr.types.path.type, mode: orr.types.modes, **options) -> orr.TopQuadrant:
        return self.orr.TopQuadrant(mode, ontology, **options)

# put path in eech mod

make = Maker()
