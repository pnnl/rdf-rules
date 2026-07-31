A slightly optionionated common set of 'rules'
for creating rdf data using 'rdf-engine':
* Data Rules:
    - table loader
    - json loader
    - ttl loader
* Mapping rule: SPARQL construct
* Ontology rules: TopQuadrant inference and validation

These rules come together in the 'engine'.

# Development
Develop with `uv sync --all-packages --all-extras`.

# Design Choices
These are choices given the common use case of mapping data.
They are somewhat firm.
- RDF1.2 annotates tripes with metadata: `<<?s ?p ?o>> ?mp ?mo `.
where `?mp` and `?mo` [correspond to simple (key,value) pairs of metadata](./src/rdf_rules/base.py).
- Mappings are in the form of SPARQL constructs stored as files with `.rq` extension (can also be `.sparql`).
- Each (specified) ontology will be processed separately

