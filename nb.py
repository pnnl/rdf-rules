import marimo

__generated_with = "0.23.14"
app = marimo.App(width="columns", auto_download=["html"])


@app.cell
def _():
    import rdf_rules.prefixes as rp
    rp.prefixes.base = 'base'
    #rp.prefixes.base = 'base2'
    #rp.prefixes.base = 'base3'
    rp.prefixes.prefixes = {'test': 'urn:xxx:yyy:zzz:' }
    rp.prefixes.prefixes 
    return


if __name__ == "__main__":
    app.run()
