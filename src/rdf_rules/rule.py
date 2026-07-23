from pyoxigraph import Store, Quad, Triple
from typing import Iterable, Callable
Triples = Iterable[Triple]
#from rdf_engine.rules import Rule #how to use the type sig?

from abc import ABC, abstractmethod
class Base(ABC):
    data_and_meta_options: dict = {'include': {'data', 'data-metaPO'} }
    """essential functionality for subclassing"""
    def __call__(self, db: Store,
          
                  ) -> Iterable[Quad]:
        data = self.data(db)
        meta = self.meta
        args = self.data_and_meta_options
        _ = (Quad(*t) for t in data_and_meta(data, meta, **args) )
        yield from _

    @abstractmethod  
    def data(self, db) -> Iterable[Triple]:
        """must implement"""
        raise NotImplementedError

    @abstractmethod
    def meta(self, triple: Triple) -> Iterable[Triple]:
        """must implement. can return empty iterable. """
        raise NotImplementedError

    # ___repr___ not 'required' but user responsibility for nicer logging



from .prefixes import prefixes
def data_and_meta(
    data: Triples,
    meta: Callable[[Triple], Triples] | None,
    meta_prefix=prefixes['meta'],
    include ={'data', 'data-metaPO'}) \
        ->Iterable[Triple]:
    class includes:
        data =       'data'
        data_meta  = 'data-metaPO'
        data_metat = 'data-meta-metatriple'
    for _ in include: assert(_ in {includes.data, includes.data_meta, includes.data_metat })
    """
    returns 
    ```
        ?s ?p ?o.                             # 'data'
    <<?s ?p ?o>> ?mp                 ?mo.   # 'data-metaPO': more immediately 'useful'
    <<?s ?p ?o>> meta:meta <<?ms ?mp ?mo>>. # 'data-meta-metatriple': most general
    ```
    Bypass associating metadata by specifying `meta=None`.
    """
    if (meta is None) and ('data' in include): yield from data
    assert(meta is not None)

    if includes.data        in include:
        yield from data
    def dms(d, ms):
        for m in ms: yield (d, m)
    def dsms(ds,):
        for d in ds:
            for d, m in dms(d, meta(d)):
                yield d, m
    # going through serialization to compactly represent meta triples
    # doing it in python is ugly
    # rdfns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    from pyoxigraph import parse, RdfFormat
    sep = '.\n'
    if includes.data_meta   in include:
        #                           dropping meta subject
        _ = sep.join(f"<<{dm[0]}>> {dm[1].predicate} {dm[1].subject}" for dm in dsms(data) )
        if _ and (not _.endswith(sep)): _ = _+sep
        _ = parse(_, format=RdfFormat.TURTLE) # ntriples doesn't do meta
        yield from _
    if includes.data_metat   in include:
        _ = sep.join(f"<<{dm[0]}>> <{meta_prefix+'meta'}> <<{dm[1]}>>" for dm in dsms(data) )
        if _ and (not _.endswith(sep)): _ = _+sep
        _ = parse(_, format=RdfFormat.TURTLE)
        yield from _
