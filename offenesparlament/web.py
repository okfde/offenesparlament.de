#coding: utf-8
from datetime import datetime

from flask import Flask, g, render_template, abort
from flask import url_for, make_response, redirect

from offenesparlament.core import app, pages, db
from offenesparlament.model import Sitzung, Ablauf
from offenesparlament.data import aggregates
from offenesparlament.views.filters import drslink
from offenesparlament.views.abo import abo
from offenesparlament.views.person import person
from offenesparlament.views.ablauf import ablauf
from offenesparlament.views.abstimmung import abstimmung
from offenesparlament.views.sitzung import sitzung
from offenesparlament.views.debatte import debatte
from offenesparlament.views.rede import rede

app.register_blueprint(abo)
app.register_blueprint(person)
app.register_blueprint(ablauf)
app.register_blueprint(abstimmung)
app.register_blueprint(sitzung)
app.register_blueprint(rede)
#app.register_blueprint(debatte)


@app.route("/pages/<path:path>")
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
    sitzung = Sitzung.query.order_by(Sitzung.nummer.desc()).first()
    return render_template('home.html', general=general,
            sachgebiete=sachgebiete, sitzung=sitzung)

if __name__ == '__main__':
    app.debug = True
    app.run(port=5006)
