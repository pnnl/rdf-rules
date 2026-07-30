from .rdf import URI
type = dict[str, URI]

common: type = {
"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
"dc": "http://purl.org/dc/elements/1.1/",
"foaf": "http://xmlns.com/foaf/0.1/",
"rdfs": "http://www.w3.org/2000/01/rdf-schema#",
"xsd": "http://www.w3.org/2001/XMLSchema#",
"owl": "http://www.w3.org/2002/07/owl#",
"vann": "http://purl.org/vocab/vann/",
"cc": "http://web.resource.org/cc/",
"vs": "http://www.w3.org/2003/06/sw-vocab-status/ns#",
"wot": "http://xmlns.com/wot/0.1/",
"geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
"inet": "http://www.w3.org/2001/02pd/rfc65#",
"dca": "http://dublincore.org/2000/03/13-dcagent#",
"uriReg": "http://www.w3.org/Addressing/schemes#",
}

def make(prefixes:type ={}, base='rdf-rules') -> type:
    _ = {'meta': f'urn:{base}:meta:',
         'data': f'urn:{base}:data:'
         }
    _ = {**_, **common, **prefixes,} # right overrides
    # 'sub' namespace to distinguish identifiers
    prefixes = {}
    for p, n in _.copy().items():
        prefixes[p+'.id'] = n+'id'
        prefixes[p] = n
    return prefixes

prefixes = make()
