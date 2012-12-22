from StringIO import StringIO
from flask import Response, url_for
from webhelpers.feedgenerator import Rss201rev2Feed

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

