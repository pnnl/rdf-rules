# no need to load in data
from pathlib import Path

class types:
    class path:
        from typing import Annotated
        from beartype.vale import Is
        type = Annotated[Path, Is[lambda p: str(p).endswith('ontology.ttl')]  ]
        # so you can have like s223-ontology.ttl if you want to distinguish
    from typing import Literal
    modes = Literal['inference'] | Literal['validation']

from pyoxigraph import Store
from .base import BaseMeta
class TopQuadrant(BaseMeta):
    def __init__(self, 
            mode: types.modes,
            ontology: types.path.type = Path('ontology'),
            additional_params = {},
                   ) -> None:
        self.mode = mode
        self.ontology = ontology
        self.additional_params = additional_params

    def params(self):
        return {
            'tqmode':   self.mode,
            'ontology': self.ontology.as_posix(),
                **self.additional_params }
    
    def data(self, db: Store):
        _ = self.source_query
        _ = db.query(_)
        tmp = Path('tq.tmp.ttl')
        if tmp.exists(): tmp.unlink()
        from pyoxigraph import serialize, RdfFormat
        from .prefixes import prefixes
        s = serialize(_,
            prefixes=prefixes,
            output=tmp, format=RdfFormat.TURTLE)
        if self.mode == 'inference':
            from pytqshacl.run import infer
            _ = infer(tmp)
        else:
            assert(self.mode == 'validation')
            from pytqshacl.run import validate
            _ = validate(tmp)
        tmp.unlink()
        from pyoxigraph import parse, RdfFormat
        _ = parse(_.stdout, format=RdfFormat.TURTLE)
        yield from _

    from functools import cached_property
    @cached_property
    def source_query(self):
        from .prefixes import prefixes as p
        _ = f"""
        prefix meta:<{p['meta']}>
        construct {{?s ?p ?o}}
        where {{
        # ontology
        {{
            << ?s ?p ?o>> meta:path ?pth.
            FILTER(lcase(STR(?pth)) = "{self.ontology.as_posix()}"  )
            }}
        # mapped data
        union
        {{
            << ?s ?p ?o>> meta:path ?pth.
            FILTER(STRENDS(lcase(STR(?pth)), ".rq") || STRENDS(lcase(STR(?pth)), ".sparql") )
            }}
        # inferred data
        union
        {{
                << ?s ?p ?o>> meta:tqmode "inference".
            }}
        }}
        """
        _ = _.split('\n')
        _ = (l.strip() for l in _)
        _ = '\n'.join(_)
        return _
