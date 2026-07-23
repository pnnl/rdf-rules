from project import project_root
from gridatlas.cache import cache as pcache # persistant cache
from functools import cached_property
from pyoxigraph import Store

_ = {_:f'urn:gk:{_}:' for _ in
    {   'data', 'meta',
        }}
std_prefixes = {
    's223': 'http://data.ashrae.org/standard223#',
    'cim':  'http://iec.ch/TC57/CIM100#',  # i think it's this
    'rdf':  'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'qudt':  'http://qudt.org/schema/qudt/',
    'qudt.unit': 'http://qudt.org/vocab/unit',
    'ct':       'https://github.com/DataTreehouse/chrontext#'
}
prefixes = std_prefixes.copy()
for k,v in _.items():
    prefixes[k] = v
    prefixes[k+'.id'] = f'{v}id:'
del _

class Data:

    class Buildings:
        path = project_root / 'data' / 'buildings_df.csv'
        @cached_property
        def df(self):
            from pandas import read_csv
            _ = read_csv(self.path)
            _ = _.convert_dtypes()
            return _
        
        @cached_property
        def json(self):
            _ = self.df
            _ = _.to_dict(orient='records')
            return _
        
        @cached_property
        def rdf(self) -> str:
            from json2rdf import j2r
            @pcache
            def bdgjson():
                return j2r(self.json,
                    subject_id_keys=('OBJECTID',),
                    id_prefix=( 'data.id',  prefixes['data.id']),
                    key_prefix=('data',     prefixes['data']),
                    )
            return bdgjson()
    buildings = Buildings()

    class Meters:
        path = project_root / 'xfmr-assignment' / 'input' / 'meters_gdf.geojson'
        @cached_property
        def json(self):
            _ = open(self.path)
            from json import load
            _ = load(_)
            return _
        
        @cached_property
        def rdf(self) -> str:
            from json2rdf import j2r
            @pcache
            def mtrjson():
                return j2r(self.json,
                    subject_id_keys=('OBJECTID',),
                    id_prefix=( 'data.id',  prefixes['data.id']),
                    key_prefix=('data',     prefixes['data']),
                    )
            return mtrjson()
    meters = Meters()

    class Transformers:
        path = project_root / 'xfmr-assignment' / 'input' / 'xfmrs_gdf.geojson'
        @cached_property
        def json(self):
            _ = open(self.path)
            from json import load
            _ = load(_)
            return _
        
        @cached_property
        def rdf(self) -> str:
            from json2rdf import j2r
            @pcache
            def mtrjson():
                return j2r(self.json,
                    subject_id_keys=('OBJECTID',),
                    id_prefix=( 'data.id',  prefixes['data.id']),
                    key_prefix=('data',     prefixes['data']),
                    )
            return mtrjson()
    transformers = Transformers()

    class MetersBuildings:
        path = project_root / 'xfmr-assignment' / 'output' / 'merged_meters_buildings.csv'
        @cached_property
        def df(self):
            from pandas import read_csv
            _ = read_csv(self.path)
            _ = _.convert_dtypes()
            # interpret in mapping
            # _ = _[['OBJECTID_x', 'OBJECTID_y']]
            # _ = _.rename({
            #     'OBJECTID_x': 'meter_id',       # bad
            #     'OBJECTID_y': 'building_id',    # bad
            #               },  axis='columns')
            # assert('meter_id')
            return _
        
        @cached_property
        def json(self):
            _ = self.df
            _ = _.to_dict(orient='records', )
            return _
        
        @cached_property
        def rdf(self) -> str:
            from json2rdf import j2r
            @pcache
            def bdgmtrjson():
                return j2r(self.json,
                    subject_id_keys=(),
                    id_prefix=( 'data.id',   prefixes['data.id']),
                    key_prefix=('data',      prefixes['data']),
                    deanon=True,
                    )
            return bdgmtrjson()
    meters_buildings = MetersBuildings()

    class BuildingsTransformers:
        path = project_root / 'xfmr-assignment' / 'output' / 'grouped_building_to_transformer_assignments.csv'
        @cached_property
        def df(self):
            from pandas import read_csv
            _ = read_csv(self.path)
            _ = _.convert_dtypes()
            return _
        
        @cached_property
        def json(self):
            _ = self.df
            _ = _.to_dict(orient='records', )
            return _
        
        @cached_property
        def rdf(self) -> str:
            from json2rdf import j2r
            @pcache
            def bdgxfmrjson():
                return j2r(self.json,
                    subject_id_keys=(),
                    id_prefix=( 'data.id',   prefixes['data.id']),
                    key_prefix=('data',      prefixes['data']),
                    deanon=True,
                    )
            return bdgxfmrjson()
    buildings_transformers = BuildingsTransformers()

    class BuildingsStock:
        # TODO: this is the same data as Buildings. can remove that data
        path = project_root / 'xfmr-assignment' / 'input' / 'buildings_elec.csv'
        @cached_property
        def df(self):
            from pandas import read_csv
            _ = read_csv(self.path)
            _ = _.convert_dtypes()
            return _
        
        @cached_property
        def json(self):
            _ = self.df
            _ = _.to_dict(orient='records', )
            return _
        
        @cached_property
        def rdf(self) -> str:
            from json2rdf import j2r
            @pcache
            def bdgstockjson():
                return j2r(self.json,
                    subject_id_keys=(),
                    id_prefix=( 'data.id',   prefixes['data.id']),
                    key_prefix=('data',      prefixes['data']),
                    deanon=True,
                    )
            return bdgstockjson()
    buildings_stock = BuildingsStock()
data = Data()


class Rules:
    @staticmethod
    def data_and_meta(ds, ms):
        #https://github.com/pnnl/BIM2RDF/blob/e4e946010c12ed92972d7d76e5a328bb424702ec/rules/src/bim2rdf/rules/rule.py#L54
        s = Store()
        from pyoxigraph import Quad
        s.bulk_extend(Quad(*t) for t in ds)
        #mv = ((m.predicate, m.object) for m in ms )
        mv = map(lambda a: f"({a[0]} {a[1]})", ms)
        mv = '\n'.join(mv)
        # making meta triples as a query instead of python
        q  = """
        construct {
        ?s ?p ?o.
        <<?s ?p ?o>> ?mp ?mo.
        }
        where {
        ?s ?p ?o.
          VALUES (?mp ?mo) {
            mv
        } }
        """
        q = q.replace('mv', mv)
        yield from (Quad(*t) for t in s.query(q))

    def data(self,):
        from pyoxigraph import parse, RdfFormat
        for d in (
            data.buildings,
            data.meters,
            data.transformers,
            data.meters_buildings,
            data.buildings_transformers,
            data.buildings_stock,
        ):
            from pyoxigraph import NamedNode, Literal
            class DataLoader:
                def __init__(self, data) -> None:
                    self.data = data
                def __repr__(self) -> str:
                    return f"{self.__class__.__name__}({self.data.path.name})"
                def __call__(self, _db):
                    _ = parse(self.data.rdf, format=RdfFormat.TURTLE)
                    _ = (t for t in _ if t.object.value != "null") # dont need nulls        
                    yield from \
                        Rules.data_and_meta(_,
                            [(NamedNode(prefixes['meta']+'name'), Literal(self.data.path.name))])
            yield DataLoader(d)


    class Ontology:
        from pathlib import Path
        path = Path(__file__).parent / 'ontology' / 'outs' / 'ontology.ttl'
        def __repr__(self) -> str:
            return f"Ontology({self.path.name})"
        def __call__(self, _db):
            from pyoxigraph import parse, RdfFormat
            _ = open(self.path)
            _ = parse(_, format=RdfFormat.TURTLE)
            from pyoxigraph import NamedNode, Literal
            yield from \
                Rules.data_and_meta(_,
                    [(NamedNode(prefixes['meta']+'name'), Literal(self.path.name))])
    ontology = Ontology()


    class Mapping:
        from pathlib import Path
        def __init__(self, q: Path) -> None:
            self.q = q
        def __repr__(self) -> str:
            return f"{self.__class__.__name__}({self.q.name})"
        def __call__(self, db):
            q = self.q.read_text()
            q =  db.query(q)
            from pyoxigraph import NamedNode, Literal
            yield from \
                Rules.data_and_meta(q,
                    [(NamedNode(prefixes['meta']+'mapping'),Literal(self.q.name))] )

            
    class TopQuadrant:
        from pathlib import Path
        from typing import Literal
        def __init__(self, run: Literal['inference'] | Literal['validation'] ) -> None:
            self.run = run
        def __repr__(self) -> str:
            return f"TopQuadrant({self.run})"
        def __call__(self, db: Store):
            _ = queries['tq.graph']
            _ = db.query(_)
            tmp = Path('tq.tmp.ttl')
            if tmp.exists(): tmp.unlink()
            from pyoxigraph import serialize, RdfFormat
            s = serialize(_,
                prefixes=prefixes,
                output=tmp, format=RdfFormat.TURTLE)
            if self.run == 'inference':
                from pytqshacl.run import infer
                _ = infer(tmp)
            else:
                assert(self.run == 'validation')
                from pytqshacl.run import validate
                _ = validate(tmp)
            tmp.unlink()
            from pyoxigraph import parse, RdfFormat
            _ = parse(_.stdout, format=RdfFormat.TURTLE)
            from pyoxigraph import NamedNode, Literal
            yield from \
                Rules.data_and_meta(_,
                    [(NamedNode(prefixes['meta']+'tqshacl'),Literal(self.run))] )
    inference  = TopQuadrant('inference')
    validation = TopQuadrant('validation')
            

    def mappings(self, ):
        from pathlib import Path
        dir = Path(__file__).parent / 'mapping'
        for m in dir.glob('**/*.rq'):
            yield self.Mapping(m)
rules = Rules()


from pathlib import Path
def map_(out=Path('db'), infer=True, validate=False):
    db = out
    db = Path(db)
    if db.exists():
        from shutil import rmtree
        rmtree(db)
    else:
        db.mkdir(exist_ok=False)
    from pyoxigraph import Store
    db = Store(db)
    from rdf_engine import Engine
    _ = [rules.ontology]+list(rules.data())
    engine = Engine(db=db, rules=_,                      derand=False,               MAX_NCYCLES=1)
    _ = engine.run()
    engine = Engine(db=_,  rules=list(rules.mappings()), derand=prefixes['meta.id'], MAX_NCYCLES=5)
    _ = engine.run()
    if infer:
        engine = Engine(db=_,  rules=[rules.inference],      derand=prefixes['meta.id'], MAX_NCYCLES=10)
        _ = engine.run()
    if validate:
        # takes too long. pending result of https://gitlab.pnnl.gov/conlight/semint/-/issues/91
        engine = Engine(db=_,  rules=[rules.validation],     derand=prefixes['meta.id'], MAX_NCYCLES=1)
        _ = engine.run()
    return Path(out)


class Queries:
    def __init__(self) -> None:
        self.path = Path(__file__).parent / 'queries'
        assert(self.path.is_dir())
    
    def __iter__(self):
        _ = self.path.glob('**/*.rq')
        for p in _: yield p.stem , open(p).read()

    def dict(self):
        return dict(self)
queries = Queries().dict()


def ttl(db=Path('db'), out=Path('model.ttl'),):
    db = Path(db)
    out = Path(out)
    assert(db.is_dir())
    from pyoxigraph import Store
    s =  Store(db)
    f = queries['mapped_and_inferred.graph']
    f = s.query(f)
    from pyoxigraph import serialize, RdfFormat
    s = serialize(f,
        prefixes=prefixes,
        output=out, format=RdfFormat.TURTLE)
    return out


def onto(out=Path('ontology.ttl')):
    out = Path(out)
    if not out.parent.exists():
        out.parent.mkdir(parents=True)
    


if __name__ == "__main__":
    class Cmds:
        map =   staticmethod(map_)
        ttl =   staticmethod(ttl)
        onto =  staticmethod(onto)
    cmds = Cmds()
    from fire import Fire
    Fire(cmds)