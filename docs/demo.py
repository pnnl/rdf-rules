import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. Provide data
    """)
    return


@app.cell
def _():
    import pandas as pd
    df = pd.read_csv('demo.csv', )
    df = df.convert_dtypes()
    for _c in df.columns:
        if df[_c].dtype == 'string':
            _ = df[_c].str.strip()
            del df[_c]
            df[_c.strip()] = _
    df
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2. Define mappings
    """)
    return


@app.cell
def _():
    import marimo as mo
    _ = open('demo.mapping.rq')
    _ = _.read()
    _ = mo.ui.code_editor(_, language='sparql')
    _
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    3. Run
    """)
    return


@app.cell
def _(df):
    from rdf_rules import mkrule
    data = mkrule(df, name='demo') # can also pass Path(demo.csv) but that would not allow the above (pre-)processing 
    from rdf_rules import run
    from pyoxigraph import Store
    from pathlib import Path
    db = run(
        # db = in memory default
        data_rules=[data],
        rules=[Path('demo.mapping.rq')],
        validate=False, infer=False)
    return (db,)


@app.cell
def _(db):
    def ttl(triples,
            prefixes={
                'foaf': 'http://xmlns.com/foaf/0.1/',
                'ppl':  'urn:example:people:'
         }):
        from pyoxigraph import serialize, RdfFormat
        _ = serialize(triples, format=RdfFormat.TURTLE, prefixes=prefixes)
        _ = _.decode()
        return _
    from rdf_rules.queries import query
    _ = query(db, 'mapped_and_inferred') # special name
    _ = ttl(_)
    print(_)
    return (ttl,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    4. Iterate
    """)
    return


@app.cell
def _(db, ttl):
    # query editing helper
    _  = open('demo.mapping.rq')
    _ = _.read()
    _ = db.query(_)
    try:
        _ = ttl(_)
    except:
        _ = map(tuple, _)
    print(_)
    return


if __name__ == "__main__":
    app.run()
