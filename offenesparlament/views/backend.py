#coding: utf-8
from collections import defaultdict
import json
from flask import Blueprint, request, url_for, flash
from flask import render_template, redirect

import sqlaload as sl 

from offenesparlament.core import db, etl_engine
from offenesparlament.util import jsonify
from offenesparlament.data.transcripts.numerge import get_alignment

backend = Blueprint('backend', __name__)

@backend.route('/backend/speechmatcher/<wp>/<session>')
def speechmatcher(wp, session):
    engine = etl_engine()
    speech_table = sl.get_table(engine, 'speech')
    speeches = sl.find(engine, speech_table, order_by='sequence', 
        wahlperiode=wp, sitzung=session, matched=True)
    webtv_table = sl.get_table(engine, 'webtv')
    agenda = sl.find(engine, webtv_table, wp=wp, session=session)
    agenda = list(agenda)
    return render_template('backend/speechmatcher.html',
            speeches=speeches, agenda=agenda, wp=wp, session=session)

@backend.route('/backend/speechmatcher/<wp>/<session>/align', methods=['GET'])
def speechmatcher_alignment_get(wp, session):
    engine = etl_engine()
    score, alignment = get_alignment(engine, wp, session)
    align_data = {}
    for align in alignment:
        seq = align.pop('sequence')
        align['matched'] = align['transcript_fp']==align['agenda_fp']
        del align['transcript_fp']
        align_data[seq] = align
    return jsonify({
        'score': score,
        'alignment': align_data
        })

@backend.route('/backend/speechmatcher/<wp>/<session>/align', methods=['POST'])
def speechmatcher_alignment_post(wp, session):
    engine = etl_engine()
    table = sl.get_table(engine, 'alignments')
    data = dict(request.form.items())
    data['sequence'] = int(data['sequence'])
    data['wp'] = wp
    data['session'] = session
    sl.upsert(engine, table, data, ['wp', 'session', 'sequence'])
    return speechmatcher_alignment_get(wp, session)

@backend.route('/backend')
def index():
    engine = etl_engine()
    webtv_table = sl.get_table(engine, 'webtv')
    sessions = sl.distinct(engine, webtv_table,
        'wp', 'session', 'session_name')
    sessions = sorted(sessions, reverse=True)
    return render_template('backend/index.html',
        sessions=sessions)
