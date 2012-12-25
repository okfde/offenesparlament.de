#coding: utf-8
from urllib import quote
from collections import defaultdict
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect, abort

from offenesparlament.core import db
from offenesparlament.lib.searcher import SolrSearcher
from offenesparlament.lib.pager import Pager
from offenesparlament.lib.seo import render_sitemap
from offenesparlament.util import jsonify
from offenesparlament.model import Sitzung, Debatte, Rede, Zitat

rede = Blueprint('rede', __name__)


@rede.route("/plenum/<wahlperiode>/<nummer>/rede/<webtv_id>")
@rede.route("/plenum/<wahlperiode>/<nummer>/rede/<webtv_id>.<format>")
def view(wahlperiode, nummer, webtv_id, format=None):
    rede = Rede.query.filter_by(webtv_id=webtv_id).first()
    if rede is None:
        abort(404)
    if format == 'json':
        return jsonify(rede)
    debatte_url = url_for('debatte.view',
            wahlperiode=rede.sitzung.wahlperiode,
            nummer=rede.sitzung.nummer,
            debatte=rede.debatte.nummer)
    return redirect(debatte_url + '#rede/' + str(rede.webtv_id))

