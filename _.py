from pathlib import Path
build_dir = Path(__file__).parent
assert('build' == build_dir.parts[-1])

cmds = {}
def register_cmd(f):
    cmds[f.__name__] = f
    return f

from pyoxigraph import Store, Quad, Triple
from typing import Iterable
Triples = Iterable[Triple]


class Base:
    def __call__(self, db: Store) -> Iterable[Quad]:
        d = self.data(db)
        #yield from d
        m = self.meta()
        yield from self.meta_and_data(d, m)

    @staticmethod
    def meta_and_data(data: Triples, meta: Triples| dict ) ->Iterable[Quad]:
        # https://github.com/pnnl/BIM2RDF/blob/e4e946010c12ed92972d7d76e5a328bb424702ec/rules/src/bim2rdf/rules/rule.py#L54-L73
        if isinstance(meta, dict): meta = Base.meta2triples(meta)
        rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        ds = Store()
        ds.bulk_extend(Quad(*t) for t in data)
        mv = ((m.predicate, m.object) for m in meta )
        mv = map(lambda a: f"({a[0]} {a[1]})", mv)
        mv = '\n'.join(mv)
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
        yield from (Quad(*t) for t in ds.query(q))
    @staticmethod
    def meta2triples(m: dict) -> Triples:
        m['id'] = 'doesntmatter'
        from json2rdf import j2r
        from semantic_explorer.prefixes import prefixes
        p = 'ts.meta'
        assert(p in prefixes)
        _ = j2r(m, key_prefix=(p, prefixes[p]))
        from pyoxigraph import RdfFormat, parse
        _ = parse(_, format=RdfFormat.TURTLE,)
        _ = (Triple(q.subject, q.predicate, q.object) for q in _ )
        _ = (t for t in _ if t.object.value != 'doesntmatter')
        yield from _



class File:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"
    def meta(self):
        return self.meta2triples({'name': self.path.name,  })
    

class TTLLoader(File, Base):
    def data(self, _: Store) -> Iterable[Quad]:
        from pyoxigraph import RdfFormat, parse
        _ = open(self.path)
        _ = parse(_, format=RdfFormat.TURTLE,)
        yield from _

class TableLoader(File, Base):
    def ttl(self,) -> Iterable[Quad]:
        if self.path.suffix.lower() == '.csv':
            from pandas import read_csv
            _ = read_csv(self.path)
            _ = _.convert_dtypes()
            _ = _.to_dict(orient='records')
        else: raise ValueError('not handled')
        from json2rdf import j2r
        from semantic_explorer.prefixes import prefixes
        idp =   'ts.anon'
        kp =    'ts'
        _ = j2r(_, 
                subject_id_keys=(), deanon=True, id_prefix=(idp, prefixes[idp]), 
                key_prefix=(kp, prefixes[kp]),
                sort=True)
        return _
        
    def data(self, _: Store) -> Iterable[Quad]:
        from pyoxigraph import RdfFormat, parse
        _ = self.ttl()
        _ = parse(_, format=RdfFormat.TURTLE,)
        yield from _


class Construct(File, Base):
    def meta(self):
        return self.meta2triples({'name': self.path.name,  })

    def data(self, db: Store) -> Iterable[Quad]:
        _ = open(self.path)
        _ = _.read()
        _ = db.query(_)
        _ = (Quad(*t) for t in _)
        yield from _

def path(p: str| Path) ->Path:
    if isinstance(p, str): p =    Path(p)
    assert(isinstance(p, Path))
    return p

@register_cmd
def mk_tsdb(data: Path, out: Path = Path('tsdb.duckdb')):
    data, out = map(path, [data, out])
    assert(out.suffix.lower() == '.duckdb')
    if not out.parent.exists():
        from shutil import rmtree
        rmtree(out.parent)
        out.mkdir(parents=True)
    if out.exists(): out.unlink()
    if 're1' in str(data).lower():
        #device_id,ts,id,data,units,type,room,zone
        import duckdb
        con = duckdb.connect(out)
        tblnm = data.stem
        # load data asis
        con.sql(f"""
            CREATE TABLE {tblnm} AS
            SELECT *
            FROM read_csv('{data}', header=True, auto_detect=True);
        """)
        # ..then create 'std' tbl
        from semantic_explorer.tsdb.chrontext import defaults
        con.sql(f"""
        CREATE view {defaults['table_name']} AS 
        SELECT id as {defaults['id_col']}, ts as {defaults['time_col']}, data as {defaults['val_col']}
        FROM  {tblnm};
        """)
    else:
        raise ValueError('not handled')
    return out


def mkdir(pth: Path):
    pth = path(pth)
    if pth.is_file():
        dir = pth.parent
    else:
        dir = pth
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@register_cmd
def map_(data: Path | str, mapping: Path | str, out=Path('db')):
    data, mapping, out = map(path, [data, mapping, out])
    assert(data.is_dir())
    assert(mapping.is_dir())
    if out.exists():
        from shutil import rmtree
        rmtree(out, )
    mkdir(out)


    from pyoxigraph import Store
    s = Store(out)
    class Rules: ...
    rules = Rules()
    rules.data =      [TTLLoader(t) for t in      data.glob('**/*.ttl')]
    l = list
    rules.data =      [TableLoader(t) for t in    l(data.glob('**/*.csv'))+l(data.glob('**/*.parquet'))] + rules.data
    rules.construct = [Construct(m)   for m in      mapping.glob('**/*.rq') ]
    
    from rdf_engine import Engine
    _ = Engine(db= s, rules=rules.data, derand=False, MAX_NCYCLES=1)
    _ = _.run()
    from semantic_explorer.prefixes import prefixes
    _ = Engine(db=_, derand=prefixes['ts.anon'],  rules=rules.construct, MAX_NCYCLES=5,)
    _ = _.run()
    return out


@register_cmd
def ttl(db: Path('db'), out = Path('data.ttl')):
    db, out = map(path, [db, out])
    q = build_dir / 'queries' / 'mapped.rq'
    q = open(q)
    q = q.read()
    db = Store(db)
    _ = db.query(q)
    from pyoxigraph import serialize
    from semantic_explorer.prefixes import prefixes
    #prefixes = {k:v for k,v in prefixes.items() if not k.startswith('bdg.') } # pyoxigraph mangles?
    serialize(_, prefixes=prefixes, output=out)
    return out


if __name__ == '__main__':
    from fire import Fire
    Fire(cmds)
