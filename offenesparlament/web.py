#coding: utf-8
from collections import defaultdict
from datetime import datetime
from urllib import quote
import re

from colander import Invalid
from jinja2 import Markup
from flask import Flask, g, request, render_template, abort, flash, json
from flask import url_for, redirect, jsonify, Response

from offenesparlament.core import app, pages, db
from offenesparlament.model import Ablauf, Position, Abstimmung, Stimme
from offenesparlament.model import Person, Gremium, Dokument
from offenesparlament.model import Sitzung, Zitat, Debatte
from offenesparlament.model import Abo

from offenesparlament.pager import Pager
from offenesparlament.util import jsonify, make_feed
from offenesparlament.searcher import SolrSearcher
from offenesparlament.abo import AboSchema, send_activation
from offenesparlament import aggregates

@app.template_filter()
def drslink(text, verbose=False):
    def r(m):
        num = m.group(1).replace(' ', '')
        dok = Dokument.query.filter_by(nummer=num).first()
        if dok is None:
            return m.group(1)
        link = "<a href='" + dok.link + "'>" + dok.nummer + "</a>"
        print dok.positionen.count()
        if verbose and dok.positionen.count() == 1:
            pos = dok.positionen.first()
            url = url_for('position', key=pos.key)
            link += " <span class='ablauf-ref'>(<a href='"+url+\
                    "'>"+pos.ablauf.titel+"</a>)</span>"
        return link
    text = re.sub(r"(\d{2,3}/\d{1,6}(\s*\(.{1,10}\))?)", r, text)
    return Markup(text)


@app.route("/plenum/<wahlperiode>/<nummer>/<debatte>")
@app.route("/plenum/<wahlperiode>/<nummer>/<debatte>.<format>")
def debatte(wahlperiode, nummer, debatte, format=None):
    debatte = Debatte.query.filter_by(nummer=debatte)\
            .join(Sitzung)\
            .filter(Sitzung.wahlperiode == wahlperiode)\
            .filter(Sitzung.nummer == nummer).first()
    if debatte is None:
        abort(404)
    if format == 'json':
        return jsonify(debatte)
    sitzung_url = url_for('sitzung', wahlperiode=wahlperiode, nummer=nummer)
    url = sitzung_url + '?debatte.titel=' + quote(debatte.titel.encode('utf-8'))
    url = url + '&paging=false'
    return redirect(url)


@app.route("/plenum/<wahlperiode>/<nummer>")
@app.route("/plenum/<wahlperiode>/<nummer>.<format>")
def sitzung(wahlperiode, nummer, format=None):
    sitzung = Sitzung.query.filter_by(wahlperiode=wahlperiode,
                                      nummer=nummer).first()
    if sitzung is None:
        abort(404)
    searcher = SolrSearcher(Zitat, request.args)
    searcher.filter('sitzung.wahlperiode', sitzung.wahlperiode)
    searcher.filter('sitzung.nummer', sitzung.nummer)
    searcher.add_facet('debatte.titel')
    searcher.add_facet('redner')
    searcher.sort('sequenz', 'asc')
    pager = Pager(searcher, 'sitzung', request.args,
            wahlperiode=wahlperiode, nummer=nummer)
    pager.limit = 100
    if format == 'json':
        data = sitzung.to_dict()
        data['results'] = pager
        return jsonify(data)
    return render_template('sitzung_view.html',
            sitzung=sitzung, pager=pager, searcher=searcher)


@app.route("/plenum")
@app.route("/plenum.<format>")
def sitzungen(format=None):
    searcher = SolrSearcher(Sitzung, request.args)
    searcher.add_facet('wahlperiode')
    searcher.sort('date', 'desc')
    pager = Pager(searcher, 'sitzungen', request.args)
    if format == 'json':
        return jsonify({'results': pager})
    return render_template('sitzung_search.html',
            searcher=searcher, pager=pager)


@app.route("/position/<key>")
@app.route("/position/<key>.<format>")
def position(key, format=None):
    position = Position.query.filter_by(key=key).first()
    if position is None:
        abort(404)
    if format == 'json':
        return jsonify(position)
    return redirect(url_for('ablauf',
        wahlperiode=position.ablauf.wahlperiode,
        key=position.ablauf.key) + '#' + position.key)


@app.route("/ablauf/<wahlperiode>/<key>")
@app.route("/ablauf/<wahlperiode>/<key>.<format>")
def ablauf(wahlperiode, key, format=None):
    ablauf = Ablauf.query.filter_by(wahlperiode=wahlperiode,
                                    key=key).first()
    if ablauf is None:
        abort(404)
    if format == 'json':
        return jsonify(ablauf)
    referenzen = defaultdict(set)
    for ref in ablauf.referenzen:
        if ref.dokument.typ == 'plpr' and ref.dokument.hrsg == 'BT':
            continue
        if ref.seiten:
            referenzen[ref.dokument].add(ref.seiten)
        else:
            referenzen[ref.dokument] = referenzen[ref.dokument] or set()
    referenzen = sorted(referenzen.items(), key=lambda (r, s): r.name)
    return render_template('ablauf_view.html',
            ablauf=ablauf, referenzen=referenzen)


@app.route("/ablauf")
@app.route("/ablauf.<format>")
def ablaeufe(format=None):
    searcher = SolrSearcher(Ablauf, request.args)
    searcher.sort('date', 'desc')
    searcher.add_facet('initiative')
    searcher.add_facet('klasse')
    searcher.add_facet('stand')
    searcher.add_facet('sachgebiet')
    searcher.add_facet('schlagworte')
    pager = Pager(searcher, 'ablaeufe', request.args)
    if format == 'json':
        return jsonify({'results': pager})
    return render_template('ablauf_search.html',
            searcher=searcher, pager=pager)


@app.route("/abstimmung/<id>")
@app.route("/abstimmung/<id>.<format>")
def abstimmung(id, format=None):
    abstimmung = Abstimmung.query.filter_by(id=id).first()
    if abstimmung is None:
        abort(404)
    ja = abstimmung.stimmen.filter(Stimme.entscheidung.like('%Ja%'))
    nein = abstimmung.stimmen.filter_by(entscheidung='Nein')
    enth = abstimmung.stimmen.filter_by(entscheidung='Enthaltung')
    na = abstimmung.stimmen.filter(Stimme.entscheidung.like('%nicht%'))

    return render_template('abstimmung_view.html',
        abstimmung=abstimmung, ja=ja, nein=nein, enth=enth, na=na)


@app.route("/gremium")
@app.route("/gremium.<format>")
def gremien(format=None):
    committees = Gremium.query.filter_by(typ='ausschuss').\
            order_by(Gremium.name.asc()).all()
    others = Gremium.query.filter_by(typ='sonstiges').\
            order_by(Gremium.name.asc()).all()
    if format == 'json':
        return jsonify({'results': committees + others})
    return render_template('gremium_list.html',
            committees=committees, others=others)


@app.route("/gremium/<key>")
@app.route("/gremium/<key>.<format>")
def gremium(key, format=None):
    gremium = Gremium.query.filter_by(key=key).first()
    if gremium is None:
        abort(404)
    if format == 'json':
        return jsonify(gremium)
    searcher = SolrSearcher(Ablauf, request.args)
    #searcher.sort('positionen.date')
    searcher.filter('positionen.zuweisungen.gremium', gremium.key)
    pager = Pager(searcher, 'gremium', request.args, key=key)
    return render_template('gremium_view.html',
            gremium=gremium, searcher=searcher, pager=pager)


@app.route("/person")
@app.route("/person.<format>")
def persons(format=None):
    searcher = SolrSearcher(Person, request.args)
    searcher.add_facet('rollen.funktion')
    searcher.add_facet('rollen.fraktion')
    searcher.add_facet('berufsfeld')
    pager = Pager(searcher, 'persons', request.args)
    if format == 'json':
        return jsonify({'results': pager})
    return render_template('person_search.html',
            searcher=searcher, pager=pager)


@app.route("/person/<slug>")
@app.route("/person/<slug>.<format>")
def person(slug, format=None):
    person = Person.query.filter_by(slug=slug).first()
    if person is None:
        abort(404)
    if format == 'json':
        return jsonify(person)
    return person_render(person, format)


@app.route("/person/mdb/<id>")
@app.route("/person/mdb/<id>.<format>")
def person_mdb(id, format=None):
    person = Person.query.filter_by(mdb_id=id).first()
    if person is None:
        abort(404)
    return person_render(person, format)


def person_render(person, format):
    searcher = SolrSearcher(Position, request.args)
    searcher.sort('date')
    searcher.filter('beitraege.person.id', str(person.id))
    pager = Pager(searcher, 'person', request.args, slug=person.slug)
    schlagworte = aggregates.person_schlagworte(person)
    debatten = Debatte.query.join(Zitat).\
            filter(Zitat.person == person).distinct().all()
    if format == 'json':
        data = person.to_dict()
        data['positionen'] = pager
        data['debatten'] = debatten
        return jsonify(data)
    elif format == 'rss':
        return make_feed(person.name, author=person.name,
            positionen=pager, debatten=debatten)
    return render_template('person_view.html',
            person=person, searcher=searcher,
            pager=pager, schlagworte=schlagworte,
            debatten=debatten[::-1])


@app.route("/person/<slug>/votes")
@app.route("/person/<slug>/votes.<format>")
def person_votes(slug, format=None):
    person = Person.query.filter_by(slug=slug).first()
    if person is None:
        abort(404)
    return render_template('person_votes.html',
            person=person)


@app.route("/abo", methods=['GET'])
def abo():
    return render_template('abo_form.html',
            fields={'query': request.args.get('query', ''),
                    'email': request.args.get('email', ''),
                    'include_activity': True,
                    'include_speeches': True
                    },
            errors={}
            )


@app.route("/abo", methods=['POST'])
def abo_post():
    schema = AboSchema()
    try:
        data = dict(request.form.items())
        data = schema.deserialize(data)
        abo_ = Abo()
        abo_.email = data['email']
        abo_.query = data['query']
        abo_.include_speeches = data['include_speeches']
        abo_.include_activity = data['include_activity']
        db.session.add(abo_)
        db.session.commit()
        send_activation(abo_)
        flash(u"Das Themen-Abo wurde erfolgreich eingerichtet. Sie erhalten nun "
              u"eine Bestätigungs-EMail.", 'success')
        return index()
    except Invalid, i:
        return render_template('abo_form.html', fields=request.form,
                errors=i.asdict())


@app.route("/abo/activate/<key>")
def abo_activation(key):
    abo = db.session.query(Abo).filter_by(activation_code=key).first()
    if abo is None:
        flash(u"Der Bestätigungscode ist ungültig oder das Abo bereits bestätigt.", 'warning')
    else:
        abo.activation_code = None
        db.session.commit()
        flash("Das Themen-Abo wurde erfolgreich eingerichtet.", 'success')
    return redirect(url_for('index'))


@app.route("/abo/lassmichinruhe/<id>")
def abo_terminate(id):
    abo = db.session.query(Abo).filter_by(id=id)\
            .filter_by(email=request.args.get('email'))
    if abo is None:
        flash(u"Abo nicht gefunden.", 'warning')
    else:
        abo.activation_code = 'deleted ' + datetime.utcnow().isoformat()
        db.session.commit()
        flash("Das Themen-Abo wurde erfolgreich gekündigt.", 'success')
    return redirect(url_for('index'))


@app.route("/pages/<path:path>")
def page(path):
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    return render_template(template, page=page)


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
