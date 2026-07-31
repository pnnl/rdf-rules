from .ontology import types as otypes
from . import prefixes as prefixesm
from pyoxigraph import Store
from typing import Any
def mkrule(a: tuple | Any, included_data={'data', 'data-metaPO' }):
    from .rule import make as mk
    if isinstance(a, tuple):
        if len(a)>1:
            if isinstance(a[-1], dict):
                p = a[:-1]
                kw = a[-1]
                _ = mk(*p, **kw)
            else:
                _ = mk(a)
        else:
            _ = mk(*a)
    else:
        _ = mk(a)
    _.data_and_meta_options = {'include': included_data }
    return _


def run(*, db = Store(),
         data_rules: list = [],
         rules: list = [],
         ontologies: list[otypes.path.type] = [],
         prefixes: prefixesm.type = {},
         use_blank_nodes: bool = False,
         infer=True, validate=True,
         included_data = {'data', 'data-metaPO' },
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
    _ = (list(mkrule(d, included_data=included_data) for d in data_rules)
         +[mkrule(o, included_data=included_data) for o in ontologies])
    from rdf_engine import Engine
    engine = Engine(db=db, rules=_, derand=False, MAX_NCYCLES=1, **logging)
    db = engine.run1()

    # RULES CYCLING
    _ = [mkrule((o, 'inference'), included_data=included_data) for o in ontologies] if infer else []
    _ = list(mkrule(r, included_data=included_data) for r in rules)+_
    engine = Engine(db=db,  rules=_, derand=derand, MAX_NCYCLES=MAX_NCYCLES, **logging)
    db = engine.run()

    # VALIDATION
    if validate:
        _ = [mkrule((o, 'validation'), included_data=included_data) for o in ontologies]
        engine = Engine(db=db,  rules=_, derand=False, MAX_NCYCLES=1, **logging)
        db = engine.run1()
    
    return db

