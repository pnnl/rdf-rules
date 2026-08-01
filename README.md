A slightly opinionated, common set of 'rules'
for creating rdf data using '[rdf-engine](https://github.com/pnnl/rdf-engine)':
* **Data Rules**: for loading tables (csv), hierarchical (json), and rdf (ttl).
* **Mapping rule**: SPARQL construct
* **Ontology rules**: Inference and validation using TopQuadrant

These rules come together in the 'engine'.

# Development
Develop with `uv sync --all-packages --all-extras`.

# Design Choices
These are choices given the common use case of mapping data to an ontology.
They are somewhat firm.
- RDF1.2 annotates tripes with metadata as `<<?s ?p ?o>> ?mp ?mo `
where `?mp` and `?mo` [correspond to simple (key,value) pairs of metadata](./src/rdf_rules/base.py).
- Mappings are in the form of SPARQL constructs
stored as files with a `.mapping.rq` extension (can also be `.mapping.sparql`).
- Each (specified) ontology will be processed separately.

# Quick Start

Examine how rules are fed into an engine in the [tests](./tests/test.py).
The common workflow is:

1. Specify rules.
Each rule is constructed by providing arguments to [`mkrule`](./src/rdf_rules/engine.py).
`mkrule` processes objects such as [file paths and data objects](./src/rdf_rules/rule.py).
A distinction is made for 'data rules';
These are only triggered once in the beginning.

2. Specify [engine run parameters](./src/rdf_rules/engine.py).
See `run` function documentation.

3. Extract data subsets with queries.
['System' queries](./src/rdf_rules/queries.py)
are `mapped_and_inferred` and `validation` (results).
It's best to extract these using the `query` function
as they slightly depend on configuration.


