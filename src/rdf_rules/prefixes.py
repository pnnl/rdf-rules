

class Prefixes:
    def __init__(self,
            base='rdf-rules',
            ) -> None:
        self._base = base
        self._prefixes = self._make_prefixes({}, base)

    # using setters and getters to keep just one global prefixes obj
    @property
    def base(self): return self._base
    @base.setter
    def base(self, new):
        self._base = new
        self.prefixes = self._make_prefixes(self.prefixes, new)
        
    @property
    def prefixes(self):
        return self._prefixes
    @prefixes.setter
    def prefixes(self, new):
        self._prefixes = self._make_prefixes(new, self.base)

    @classmethod
    def _make_prefixes(cls, prefixes, base):
        _ = {
            'meta': f'urn:{base}:meta:'
        }
        _ = {**_, **prefixes,} # prefixes overrides
        # 'sub' namespace to distinguish identifiers
        prefixes = {}
        for p, n in _.copy().items():
            prefixes[p+'.id'] = n+'id'
            prefixes[p] = n
        return prefixes

prefixes = Prefixes()
