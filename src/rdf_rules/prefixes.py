
from .rdf import URI

type = dict[str, URI]
def make(prefixes:type ={}, base='rdf-rules') -> type:
    _ = {'meta': f'urn:{base}:meta:',
         'data': f'urn:{base}:data:'
         }
    _ = {**_, **prefixes,} # prefixes overrides
    # 'sub' namespace to distinguish identifiers
    prefixes = {}
    for p, n in _.copy().items():
        prefixes[p+'.id'] = n+'id'
        prefixes[p] = n
    return prefixes

prefixes = make()
