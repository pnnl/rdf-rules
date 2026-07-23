import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import rdf_rules.prefixes as rp
    rp.prefixes
    return


@app.cell
def _():

    import rdf_rules.rule as rr

    class TestBase(rr.Base):
        def data(self, db):
            _ = """
            # --- Prefixes to shorten URIs ---
            @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd:  <http://w3.org> .
            @prefix foaf: <http://xmlns.com> .
            @prefix ex:   <http://example.org> .
            ex:alice123
                rdf:type foaf:Person ;
                foaf:name "Alice Smith"^^xsd:string ;
                foaf:age 30 ; .
            """
            from pyoxigraph import parse, RdfFormat
            _ =  parse(_, format=RdfFormat.TURTLE)
            return list(_)
            #for t in _: yield t
        def meta(self, t):
            _ = """
            # --- Prefixes to shorten URIs ---
            @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd:  <http://w3.org> .
            @prefix foaf: <http://xmlns.com> .
            @prefix ex:   <http://example.org> .
            ex:metas ex:metap ex:metao.
            """
            from pyoxigraph import parse, RdfFormat
            _ =  parse(_, format=RdfFormat.TURTLE)
            _ = list(_)
            assert(len(_) == 1)
            return _

    b = TestBase()
    _ = b.data_and_meta(b.data(''), b.meta,
            include={
                #'data',
                'data-metaPO',
                #'data-meta-metatriple'
            })
    _ = list(_)
    _
    return


if __name__ == "__main__":
    app.run()
