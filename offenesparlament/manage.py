from flask.ext.script import Manager

from offenesparlament.core import app, etl_engine, solr
from offenesparlament.web import app
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.threaded import process

from offenesparlament.data.persons import PERSON
from offenesparlament.data.gremien import GREMIUM
from offenesparlament.data.abstimmungen import ABSTIMMUNG
from offenesparlament.data.transcripts import TRANSCRIPT
from offenesparlament.data.ablaeufe import ABLAUF
import logging
log = logging.getLogger(__name__)

manager = Manager(app)


def _stage(proc, url=None, force=False, threaded=False, preload=True):
    app.config['NOMENKLATURA_PRELOAD'] = preload
    indexer = get_indexer()
    try:
        if url is None:
            process(indexer, proc, force=force,
                    threaded=threaded)
        else:
            engine = etl_engine()
            proc['handler'](engine, indexer, url,
                            force=force)
    finally:
        indexer.flush()


@manager.command
def download_docs():
    """ Download all PDFs from DIP. """
    engine = etl_engine()
    from offenesparlament.extract import documents
    documents.load_documents(engine)


@manager.command
def persons(url=None, force=False, threaded=False, preload=False):
    """ Load all or a specific person. """
    _stage(PERSON, url=url, force=force, threaded=threaded,
            preload=not preload)


@manager.command
def gremien(url=None, force=False, threaded=False, preload=False):
    """ Load all or a specific committee. """
    _stage(GREMIUM, url=url, force=force, threaded=threaded,
            preload=not preload)


@manager.command
def abstimmungen(url=None, force=False, threaded=False, preload=False):
    """ Load all or a specific vote. """
    _stage(ABSTIMMUNG, url=url, force=force, threaded=threaded,
            preload=not preload)


@manager.command
def transcripts(url=None, force=False, threaded=False, preload=False):
    """ Load all or a specific transcript. """
    _stage(TRANSCRIPT, url=url, force=force, threaded=threaded,
            preload=not preload)


@manager.command
def ablaeufe(url=None, force=False, threaded=False, preload=False):
    """ Load all or a specific proceeding. """
    _stage(ABLAUF, url=url, force=force, threaded=threaded,
            preload=not preload)


@manager.command
def update(force=False, threaded=False, preload=False):
    """ Update the entire database. """
    app.config['NOMENKLATURA_PRELOAD'] = not preload
    indexer = get_indexer()
    try:
        for stage in [GREMIUM, PERSON, ABSTIMMUNG, ABLAUF, TRANSCRIPT]:
            process(indexer, stage, force=force,
                    threaded=threaded)
            log.debug("Finish updating: %s" % stage)
    finally:
        indexer.flush()


@manager.command
def dumpindex():
    """ Destroy the FTS index. """
    _solr = solr()
    _solr.delete_query("*:*")
    _solr.commit()


@manager.command
def aggregate():
    from offenesparlament.data.aggregates import make_current_schlagwort, \
        make_period_sachgebiete, make_person_schlagworte
    make_current_schlagwort()
    make_period_sachgebiete()
    make_person_schlagworte()


@manager.command
def notify():
    from offenesparlament.lib.abo import notify
    notify()


if __name__ == "__main__":
    manager.run()
