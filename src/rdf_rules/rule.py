from pyoxigraph import Store, Quad, Triple
from typing import Any
from collections.abc import Callable, Iterable
Triples = Iterable[Triple]
#from rdf_engine.rules import Rule #how to use the type sig?

from abc import ABC, abstractmethod
class Base(ABC):
    data_and_meta_options: dict = {'include': {'data', 'data-metaPO'} }
    """essential functionality for subclassing"""
    def __call__(self, db: Store = Store(),
          
                  ) -> Iterable[Quad]:
        data = self.data(db)
        meta = self.meta
        args = self.data_and_meta_options
        _ = (Quad(*t) for t in data_and_meta(data, meta, **args) )
        yield from _

    @abstractmethod  
    def data(self, db) -> Iterable[Triple]:
        """must implement. it must always produce data."""
        raise NotImplementedError

    @abstractmethod
    def meta(self, data_triple: Triple) -> Iterable[Triple]:
        """must implement. can return empty iterable. """
        raise NotImplementedError

    @abstractmethod
    def params(self) -> dict[str, Any]:
        """must implement. """
        raise NotImplementedError

    def __repr__(self) -> str:
        p = ','.join(f"{k}={v}" for k,v in self.params().items() )
        return f"{self.__class__.__name__}({p})"


class BaseMeta(Base):
    """
    mixin for typical meta handling
    where params are simple (key,value) pairs.
    """
    data_and_meta_options: dict = {'include': {'data', 'data-metaPO'} }

    from functools import cache
    @cache
    def _constmeta(self, ) -> Triples:
        # 'const'ant, does not depend on data
        assert('data-metaPO' in self.data_and_meta_options['include'])
        _ = self.params()
        from json2rdf import json2rdf as j2r
        _ = j2r(_, subject_id_keys={}, # doesn't matter b/c subject will be stripped
                key_prefix=('p', prefixes['meta'] ),
                )
        from pyoxigraph import parse, RdfFormat
        _ = parse(_, RdfFormat.TURTLE)
        _ = frozenset(_)    # not generator
        return _            # not generator
    
    def meta(self, data_triple) -> Triples:
        _ =  self._constmeta()
        yield from _ 


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
        # need to keep around data if it's a gen
        if any(i in {includes.data_meta, includes.data_metat} for i in include):
            from collections.abc import Iterator
            if isinstance(data, Iterator):
                data = frozenset(data)
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
        _ = sep.join(f"<<{dm[0]}>> {dm[1].predicate} {dm[1].object}" for dm in dsms(data) )
        if _ and (not _.endswith(sep)): _ = _+sep
        _ = parse(_, format=RdfFormat.TURTLE) # ntriples doesn't do meta
        yield from _
    if includes.data_metat   in include:
        _ = sep.join(f"<<{dm[0]}>> <{meta_prefix+'meta'}> <<{dm[1]}>>" for dm in dsms(data) )
        if _ and (not _.endswith(sep)): _ = _+sep
        _ = parse(_, format=RdfFormat.TURTLE)
        yield from _
