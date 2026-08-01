from ..base import BaseMeta as _BaseMeta
from ..base import Quads, Triple

null = 'null'

class BaseMeta(_BaseMeta):
    null_values = {}

    from pyoxigraph import Store
    def __call__(self, db = Store()) -> Quads:
        qs = super().__call__(db)
        nv = self.null_values
        if not nv: yield from qs

        from pyoxigraph import NamedNode
        refies = NamedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#"+'reifies')
        def isnested(t, rt=refies):
            if isinstance(t.object, Triple):
                # nested/reifying  triple https://www.w3.org/TR/rdf12-concepts/#dfn-reifying-triple
                if (t.predicate == rt):
                    return True
                else:
                    raise ValueError('(subject, not rdf:reifies, triple) not handled')
            else:
                return False

        def hasnull(o):
            if isinstance(o, Literal):
                v = o.value
                if isinstance(v, str):
                    if v in nv:
                        return True
            return False

        from pyoxigraph import Literal
        for q in qs:
            t = q.triple
            if isnested(t):
                o = t.object.object
            else:
                o = t.object
            if not hasnull(o):
                yield q
            

                

