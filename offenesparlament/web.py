#coding: utf-8
from datetime import datetime
from hashlib import sha1

from flask import Flask, g, render_template, abort, request
from flask import url_for, make_response, redirect, Response

from offenesparlament.core import app, pages, db
from offenesparlament.model import Sitzung, Ablauf
from offenesparlament.data import aggregates
from offenesparlament.util import validate_cache, NotModified
from offenesparlament.views.filters import drslink
from offenesparlament.views.abo import abo
from offenesparlament.views.person import person
from offenesparlament.views.ablauf import ablauf
from offenesparlament.views.abstimmung import abstimmung
from offenesparlament.views.sitzung import sitzung
from offenesparlament.views.debatte import debatte
from offenesparlament.views.rede import rede
from offenesparlament.views.backend import backend

app.register_blueprint(abo)
app.register_blueprint(person)
app.register_blueprint(ablauf)
app.register_blueprint(abstimmung)
app.register_blueprint(sitzung)
app.register_blueprint(rede)
app.register_blueprint(debatte)
app.register_blueprint(backend)


@app.before_request
def setup_cache():
    args = request.args.items()
    args = filter(lambda (k,v): k != '_', args) # haha jquery where is your god now?!?
    query = sha1(repr(sorted(args))).hexdigest()
    request.cache_key = {'query': query}
    request.no_cache = False

@app.after_request
def configure_caching(response_class):
    if not app.config.get('CACHE'):
        return response_class
    if request.no_cache:
        return response_class
    if request.method in ['GET', 'HEAD', 'OPTIONS'] \
        and response_class.status_code < 400:
        try:
            etag, mod_time = validate_cache(request)
            response_class.add_etag(etag)
            response_class.cache_control.max_age = app.config.get('CACHE_AGE')
            response_class.cache_control.public = True
            if mod_time:
                response_class.last_modified = mod_time
        except NotModified:
            return Response(status=304)
    return response_class

@app.route("/info/<path:path>")
def page(path):
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    return render_template(template, page=page)


@app.route("/sitemap.xml")
def sitemap():
    now = datetime.utcnow()
    years = range(2000, now.year+1)[::-1]
    res = make_response(render_template('sitemapindex.xml',
        years=years, now=now, url=url_for('index', _external=True)))
    res.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return res

@app.route("/robots.txt")
def robots_txt():
    res = make_response(render_template('robots.txt'))
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

@app.route("/favicon.ico")
def favicon_ico():
    return redirect('/static/favicon.ico', code=301)

@app.route("/")
def index():
    general = aggregates.current_schlagworte()
    sachgebiete = aggregates.sachgebiete()
    request.cache_key['general'] = general
    request.cache_key['sachgebiete'] = sachgebiete
    return render_template('home.html', general=general,
            sachgebiete=sachgebiete)

if __name__ == '__main__':
    app.debug = True
    app.run(port=5006)

