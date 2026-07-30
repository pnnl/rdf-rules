from pathlib import Path
test_dir = Path(__file__).parent.relative_to(Path('.').absolute())
data_dir = test_dir / 'data'
import pytest
regression = "regression"
@pytest.fixture(scope="session")
def lazy_datadir() -> Path:
    return data_dir / regression
@pytest.fixture(scope="session")
def original_datadir() -> Path:
    return data_dir / regression

from rdflib import Graph
def is_eq(g1: Graph|str, g2: Graph|str):
    from rdflib import Graph
    g1 = Graph().parse(data=g1, format='text/turtle') if isinstance(g1, str) else g1
    g2 = Graph().parse(data=g2, format='text/turtle') if isinstance(g2, str) else g2
    from rdflib.compare import isomorphic
    return isomorphic(g1, g2)

def check_fn(obtained_fn, expected_fn):
    o, e = map(lambda f: open(f).read(), (obtained_fn, expected_fn))
    if not is_eq(o, e): raise AssertionError
    # for file_regression.check(r, check_fn=check_fn, extension='.ttl')


def unstar(ts):
    from rdf_engine.data import reification
    return reification.standard(ts)

def serialize(ts):
    _ = ts
    _ = unstar(_)
    from rdflib import Graph
    g = Graph()
    sep = '.\n'
    _ = sep.join(str(t) for t in _ )
    if _:
        if not _.endswith(sep):
            _ = _ + sep
    g.parse(data=_, format='nt')
    _ = g.serialize(format='turtle')
    return _


import rdf_rules.rule as rule

import rdf_rules.data.table as rt
import pandas as pd
@pytest.mark.parametrize('table',[
            (pd.read_csv(Path(data_dir / 'test.csv')), {'name': 'test'}),   # 0
            (Path(data_dir / 'test.csv'),  {}),                             # 1
            ] )
def test_table(table, file_regression):
    p, kw = table
    data(rule.make(p, **kw), file_regression)

def data(rule, file_regression):
    _ = rule()
    _ = rule()  # twice to make sure it returns data
    _ = serialize(_)
    assert(len(_)>5)
    file_regression.check(_, check_fn=check_fn, extension='.ttl')

from json import load as jload
import rdf_rules.data.json as rj
@pytest.mark.parametrize('json',[
            (rj.Str(open(Path(data_dir / 'test.json')).read()), {'name': 'test', 'additional_params': {'additionalk':'additionalv'} }),
            (jload(open(Path(data_dir / 'test.json'))), {'name': 'test', 'additional_params': {'additionalk':'additionalv'} }), 
            (Path(data_dir / 'test.json'),  {}),                                                                                
            ] )
def test_json(json, file_regression):
    p, kw = json
    data(rule.make(p, **kw), file_regression)


# todo: could be just test_rule
