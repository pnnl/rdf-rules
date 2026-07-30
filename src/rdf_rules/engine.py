# typical engine: a bit opinionated
# - datarules
# - other rule
# - ontology rules. (applying  each one separately.)
    # - infer
    # - validate
from rdf_engine.rules import Rule
from .ontology import Path as OntoPath
from . import prefixes as prefixesm

def make(*,
         datarules: list[Rule],
         rules: list[Rule],
         ontologies: list[OntoPath],
         prefixes: prefixesm.type = {},
         use_blank_nodes: bool = False,
             ):
    prefixesm.prefixes = prefixesm.make(prefixes)
    # load each ontology in data rule
