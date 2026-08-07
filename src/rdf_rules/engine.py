from .ontology import types as otypes
from . import prefixes as prefixesm
from pyoxigraph import Store
from typing import Any
from collections.abc import Callable
from rdf_engine.rules import Rule
RuleData = set | frozenset | Callable[[Rule], set | frozenset ]

def mkrule(a: tuple | Any,
        included_data: RuleData={'data', 'data-metaPO' } ,
        null_values = {'null'},
          ):
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

    if isinstance(included_data, (set, frozenset) ):
        _.data_and_meta_options = {'include': included_data }
    else:
        assert(callable(included_data))
        _.data_and_meta_options = {'include': included_data(_) }

    from .data.base import BaseMeta as DataRule
    if isinstance(_, DataRule):
        _.null_values =  null_values
        
    return _


def run(*, db = Store(),
         data_rules: list = [],
         rules: list = [],
         ontologies: list[otypes.path.type] = [],
         prefixes: prefixesm.type = {},
         use_blank_nodes: bool = True,
         infer=True, validate=True,
         included_data: RuleData = {'data', 'data-metaPO' },
         null_values = {}, remove_null=True,
         MAX_NCYCLES=10,
         log_data: bool=True, log_print: bool=True, log_debug: bool=False,
             ) -> Store:
    """
    The defaults are the most conservative and functional settings.
    Relax them for more performance but consider the drawbacks.

    use_blank_nodes: If this is False
        and you use generated blank nodes in the cycling 'rules' phase,
        the process will not complete since they are different in each cycle.
        This can be mitigated by setting this parameter to True
        but at a high performance expense.
    included_data: is the set of data each rule is allowed to pass:
        'data': 'regular' triples: `?s ?p ?o`.
        'data-metaPO': data triples plus metadata in the form `<<?s ?p ?o>> ?mp ?mo`.
        Typical use assumes both.
        The metadata is essential for inferencing and validation.
        But, using metadata increases the size of the db significantly
        incurring a performance cost.
        For more control, this can be a function that takes the rule as an argument
        and returns the set.
    
    remove_null: If True, adds 'null' to null_values.
        'null' is special as it is considered the canonical null value.
        This is applied to `data_rules` (but not RDF readers).
    
    """
    logging = {'log_data': log_data, 'log_print': log_print, 'log_debug': log_debug}
    # typical engine: a bit opinionated
    prefixesm.prefixes = prefixesm.make(prefixes)
    if use_blank_nodes:
        derand = 'canonicalize'
    else:
        derand = prefixesm.prefixes['anon.id']
    
    if remove_null:
        from .data.base import null
        null_values = frozenset(null_values) | {null}

    # DATA LOADING
    # load each ontology in data rule
    _ = (list(mkrule(d, included_data=included_data, null_values=null_values) for d in data_rules)
         +[mkrule(o, included_data=included_data,) for o in ontologies])
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

