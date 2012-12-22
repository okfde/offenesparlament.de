import json
from datetime import datetime
from StringIO import StringIO

from flask import Response, request, url_for
from webhelpers.feedgenerator import Rss201rev2Feed

from offenesparlament.pager import Pager

class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def encode(self, obj):
        if hasattr(obj, 'to_dict'):
            obj = obj.to_dict()
        return super(JSONEncoder, self).encode(obj)

    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Pager):
            return list(obj)
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        raise TypeError("%r is not JSON serializable" % obj)


def jsonify(obj, status=200, headers=None):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    jsondata = json.dumps(obj, cls=JSONEncoder)
    if 'callback' in request.args:
        jsondata = '%s(%s)' % (request.args.get('callback'), jsondata)
    return Response(jsondata, headers=headers,
                    status=status, mimetype='application/json')


def make_feed(title, author='OffenesParlament.de',
    positionen=[], debatten=[], limit=10):
    items = []
    for position in positionen:
        ablauf = position.ablauf
        items.append({
            'title': '[Drs] ' + position.typ + ': ' + position.ablauf.titel,
            'pubdate': position.date,
            'link': url_for('ablauf.view',
                wahlperiode=position.ablauf.wahlperiode,
                key=position.ablauf.key,
                _external=True) + '#' + position.key,
            'description': position.ablauf.abstrakt
            })
    for debatte in debatten:
        if debatte.nummer is None:
            continue
        items.append({
            'title': '[Rede] ' + debatte.titel,
            'pubdate': debatte.sitzung.date,
            'link': url_for('debatte', wahlperiode=debatte.sitzung.wahlperiode,
                nummer=debatte.sitzung.nummer, debatte=debatte.nummer,
                _external=True),
            'description': debatte.text
            })
    feed = Rss201rev2Feed(title, url_for('index', _external=True), 
        'Was passiert im Bundestag?', author_name=author)
    items = sorted(items, key=lambda i: i.get('pubdate').isoformat(), reverse=True)
    for item in items[:10]:
        feed.add_item(**item)
    sio = StringIO()
    feed.write(sio, 'utf-8')
    return Response(sio.getvalue(), status=200, mimetype='application/xml')

