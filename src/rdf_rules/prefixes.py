

def make(prefixes={}, base='rdf-rules'):
    _ = {'meta': f'urn:{base}:meta:'}
    _ = {**_, **prefixes,} # prefixes overrides
    # 'sub' namespace to distinguish identifiers
    prefixes = {}
    for p, n in _.copy().items():
        prefixes[p+'.id'] = n+'id'
        prefixes[p] = n
    return prefixes

prefixes = make()
