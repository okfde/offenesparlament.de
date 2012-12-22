#coding: utf-8
from urllib import quote
from collections import defaultdict
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect

from offenesparlament.core import db
from offenesparlament.lib.searcher import SolrSearcher
from offenesparlament.lib.pager import Pager
from offenesparlament.lib.seo import render_sitemap
from offenesparlament.util import jsonify
from offenesparlament.model import Sitzung, Debatte

debatte = Blueprint('debatte', __name__)


@debatte.route("/plenum/<wahlperiode>/<nummer>/<debatte>")
@debatte.route("/plenum/<wahlperiode>/<nummer>/<debatte>.<format>")
def view(wahlperiode, nummer, debatte, format=None):
    debatte = Debatte.query.filter_by(nummer=debatte)\
            .join(Sitzung)\
            .filter(Sitzung.wahlperiode == wahlperiode)\
            .filter(Sitzung.nummer == nummer).first()
    if debatte is None:
        abort(404)
    if format == 'json':
        return jsonify(debatte)
    sitzung_url = url_for('sitzung.view', wahlperiode=wahlperiode, nummer=nummer)
    url = sitzung_url + '?debatte.titel=' + quote(debatte.titel.encode('utf-8'))
    url = url + '&paging=false'
    return redirect(url)

