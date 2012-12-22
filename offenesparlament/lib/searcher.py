import json 

from offenesparlament.core import solr

EXLUDE_FILTERS = ['limit', 'page', 'q', 'callback', '_', 'paging']

class SolrSearcher(object):

    def __init__(self, type_, args):
        self.type_ = type_
        self.args = args
        self.results = None
        self._offset = 0
        self._filters = []
        self._facets = []
        self._limit = 9001
        self._sort = 'score desc'

    def sort(self, field, order='desc'):
        self._sort = field + ' ' + order

    @property
    def has_query(self):
        return len(self.q.strip()) > 0

    @property
    def q(self):
        return self.args.get('q', '')

    def limit(self, limit):
        self.results = None
        self._limit = limit
        return self

    def offset(self, offset):
        self.results = None
        self._offset = offset
        return self

    def add_facet(self, facet):
        self.results = None
        self._facets.append(facet)

    def facet_values(self, facet):
        if self.results is None:
            self._run()
        values = self.results.get('facet_counts', {}).get('facet_fields',
                {}).get(facet, [])
        options = []
        for value in values[::2]:
            count = values[values.index(value)+1]
            options.append((value, count))
        return options

    def has_facet(self, facet):
        return self.facet_values(facet) > self.args.getlist(facet)
    
    def filter(self, key, value):
        self._filters.append((key, value))

    @property
    def query_filters(self):
        _filters = []
        for k, v in self.args.items():
            if k in EXLUDE_FILTERS:
                continue
            _filters.append((k, v))
        return _filters

    @property
    def filters(self):
        _filters = [('index_type', self.type_.__name__.lower())]
        _filters.extend(self.query_filters)
        _filters.extend(self._filters)
        return _filters

    @property
    def fq(self):
        _fqs = []
        for k, v in self.filters:
            if v is None:
                continue
            v = unicode(v).replace("\"", "'")
            _fqs.append("+%s:\"%s\"" % (k, v))
        return _fqs

    @property
    def full_query(self):
        q = self.q if self.has_query else ''
        if len(self.fq):
            fq = [f for f in self.fq if not 'index_type' in f]
            q += ' ' + ' '.join(fq)
        return q

    def _run(self):
        query = {
            'q': self.q if self.has_query else '*:*',
            'fq': self.fq,
            'rows': self._limit,
            'start': self._offset,
            'facet': 'true',
            'facet_limit': 100,
            'facet_mincount': 1,
            'facet_sort': 'count',
            'facet_field': self._facets,
            'wt': 'json',
            'fl': 'id score',
            'sort': self._sort
            }
        response = solr().raw_query(**query)
        self.results = json.loads(response)

    def all(self):
        if self.results is None:
            self._run()
        docs = self.results.get('response', {}).get('docs')
        ids = [int(d['id']) for d in docs]
        if not len(ids):
            return []
        objs = self.type_.query.filter(
                self.type_.id.in_(ids)).all()
        objs = dict([(o.id, o) for o in objs])
        return [objs[id] for id in ids]

    def count(self):
        if self.results is None:
            self._run()
        return self.results.get('response', {}).get('numFound')

