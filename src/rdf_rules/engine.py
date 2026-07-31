from .ontology import types as otypes
from . import prefixes as prefixesm
from pyoxigraph import Store
from typing import Any
def mkrule(a: tuple | Any):
    from .rule import make as mk
    if isinstance(a, tuple):
        if len(a)>1:
            if isinstance(a[-1], dict):
                p = a[:-1]
                kw = a[-1]
                return mk(*p, **kw)
            else:
                return mk(a)
        else:
            return mk(*a)
    else:
        return mk(a)


def run(*, db = Store(),
         data_rules: list = [],
         rules: list = [],
         ontologies: list[otypes.path.type] = [],
         prefixes: prefixesm.type = {},
         use_blank_nodes: bool = False,
         infer=True, validate=True,
         MAX_NCYCLES=10,
         log_data: bool=True, log_print: bool=True, log_debug: bool=False,
             ):
    logging = {'log_data': log_data, 'log_print': log_print, 'log_debug': log_debug}
    # typical engine: a bit opinionated
    prefixesm.prefixes = prefixesm.make(prefixes)
    if use_blank_nodes:
        derand = 'canonicalize'
    else:
        derand = prefixesm.prefixes['anon.id']

    # DATA LOADING
    # load each ontology in data rule
    _ = list(mkrule(d) for d in data_rules)+[mkrule(o) for o in ontologies]
    from rdf_engine import Engine
    engine = Engine(db=db, rules=_, derand=False, MAX_NCYCLES=1, **logging)
    db = engine.run1()

    # RULES CYCLING
    _ = [mkrule((o, 'inference')) for o in ontologies] if infer else []
    _ = list(mkrule(r) for r in rules)+_
    engine = Engine(db=db,  rules=_, derand=derand, MAX_NCYCLES=MAX_NCYCLES, **logging)
    db = engine.run()

    # VALIDATION
    if validate:
        _ = [mkrule((o, 'validation')) for o in ontologies]
        engine = Engine(db=db,  rules=_, derand=False, MAX_NCYCLES=1, **logging)
        db = engine.run1()
    
    return db

