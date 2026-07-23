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
