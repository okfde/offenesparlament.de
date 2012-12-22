from datetime import datetime
from flask import render_template, make_response

def render_sitemap(items, prio=0.8):
    items_ = []
    for item in items:
        item['lastmod'] = min(item.get('lastmod'), datetime.now())
    res = make_response(render_template('sitemap.xml',
        items=items, prio=prio))
    res.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return res


