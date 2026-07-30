from pathlib import Path

class Str(str): ...

class path:
    from typing import Annotated
    from beartype.vale import Is
    type = Annotated[Path, Is[lambda p: p.suffix in {'.sparql', '.rq'}]]


from .base import BaseMeta
class ConstructQuery(BaseMeta):
    def __init__(self, *, query: Str | None = None, path: path.type | None = None,
            name: str | None = None,
            additional_params = {},):
        assert(query or path)
        assert(not (query and path))
        self.path = path
        self.name = name
        self.query = query if query else path.read_text()
        if (name is None) and (path is None):
            import hashlib
            self.name = hashlib.sha1(query.encode('utf-8')).hexdigest()
        self.additional_params = additional_params

    from pyoxigraph import Store
    def data(self, db: Store=Store()):
        q = self.query
        _ = db.query(q)
        yield from _

    def params(self):
        name = {'name': self.name} if self.name else {}
        path = {'path': self.path.as_posix()} if self.path else {}
        return {**name, **path,
                **self.additional_params }

