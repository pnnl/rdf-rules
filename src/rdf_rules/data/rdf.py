from collections.abc import Callable
from pathlib import Path

class paths:
    class type:
        from typing import Annotated
        from beartype.vale import Is
        ttl = Annotated[Path, Is[lambda p: p.suffix == '.ttl']]

from ..base import BaseMeta
class TTL(BaseMeta):
    class type:
        class Str(str):...

    def __init__(self, ttl: Callable[[], type.Str] | type.Str,
            name: str | None = None, *,
            additional_params = {},
                 ) -> None:
        self._ttl = ttl
        self.name = name if name else str(id(name))
        self.additional_params = additional_params


    #from functools import cache
    #@cache
    def ttl(self) -> type.Str:
        if callable(self._ttl):
            _ = self._ttl()
        else:
            _ = self._ttl
        _ = self.type.Str(_)
        return _

    def data(self, db):
        _ = db
        _ = self.ttl()
        from pyoxigraph import parse, RdfFormat
        _ = parse(_ , format=RdfFormat.TURTLE)
        yield from _

    def params(self):
        _ =  {'name': self.name,
                **self.additional_params }
        return _
        

class TTLReader(BaseMeta):
    def __init__(self, path: paths.type.ttl,
            additional_params = {},
                 ) -> None:
        self.path = path
        self.additional_params = additional_params
        self.ttl = TTL(lambda: TTL.type.Str(open(path).read()))

    def params(self):
        _ = {'path': self.path.as_posix(),# could do name but path is good enough
             **self.additional_params,
              } 
        return _

    def data(self, db):
        _ = db
        return self.ttl.data(_)

