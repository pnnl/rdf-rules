from pathlib import Path
test_dir = Path(__file__).parent
import pytest

@pytest.fixture(scope="session")
def lazy_datadir() -> Path:
    return test_dir / "regression_data"
@pytest.fixture(scope="session")
def original_datadir() -> Path:
    return test_dir / "regression_data"

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


import pandas as pd
@pytest.mark.parametrize('table',[
                        #Path('test.csv'),
            pd.read_csv(Path('test.csv')) 
            ] )
def test_table(table, file_regression):
    t = table
    import rdf_rules.data.table as rt
    tr = rt.Table(t)
    _ = tr()
    _ = serialize(_)
    file_regression.check(_, check_fn=check_fn, extension='.ttl')
