[Documentation](http://pnnl.github.io/rdf-rules)


A slightly opinionated, common set of 'rules'
for creating rdf data using '[rdf-engine](https://github.com/pnnl/rdf-engine)':
* **Data Rules**: for loading tables (csv), hierarchical (json), and rdf (ttl).
* **Mapping rule**: SPARQL construct
* **Ontology rules**: Inference and validation using [Shifty](https://shifty.gtf.fyi/)

These rules come together in the 'engine'.

# Development

History/context:
This framework is a generalization of [BIM2RDF](https://github.com/pnnl/BIM2RDF).

Develop with `uv sync --all-packages --all-extras`.

Run `python tasks.py stamp_ver` before pypi publishing.

# Design Choices

These are choices given the common use case of mapping data to an ontology.
They are somewhat firm.
- RDF1.2 annotates tripes with metadata as `<<?s ?p ?o>> ?mp ?mo `
where `?mp` and `?mo` [correspond to simple (key,value) pairs of metadata](./src/rdf_rules/base.py).
- Mappings are in the form of SPARQL constructs
stored as files with a `.mapping.rq` extension (can also be `.mapping.sparql`).
- Each (specified) ontology will be processed separately.
- By default, no assumption about data identifier uniqueness is made:
A random unique identifier node,
with the default 'anon.id' prefix 'urn:rdf-rules:anon:id:',
will be created to identify data (table 'rows' or json data).
It is the user's responsibility to make 'nice' named nodes:
This can be by making a 'rule' to SPARQL `construct` nodes
or by specifying 
`json2rdf_options={'subject_id_keys': {'id'}, id_prefix=(..., ...) }`
argument for Table or JSON data rules.
With these options, nodes can be made unique over all data.

# Usage

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

