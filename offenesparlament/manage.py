from flaskext.script import Manager

from offenesparlament.core import app, etl_engine, solr
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.threaded import process

from offenesparlament.data.persons import PERSON
from offenesparlament.data.gremien import GREMIUM
from offenesparlament.data.abstimmungen import ABSTIMMUNG
from offenesparlament.data.transcripts import TRANSCRIPT
from offenesparlament.data.ablaeufe import ABLAUF

manager = Manager(app)


def _stage(proc, url=None, force=False, threaded=False):
    engine = etl_engine()
    indexer = get_indexer()
    try:
        if url is None:
            process(engine, indexer, proc, force=force,
                    threaded=threaded)
        else:
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
def persons(url=None, force=False, threaded=False):
    """ Load all or a specific person. """
    _stage(PERSON, url=url, force=force, threaded=threaded)


@manager.command
def gremien(url=None, force=False, threaded=False):
    """ Load all or a specific committee. """
    _stage(GREMIUM, url=url, force=force, threaded=threaded)


@manager.command
def abstimmungen(url=None, force=False, threaded=False):
    """ Load all or a specific vote. """
    _stage(ABSTIMMUNG, url=url, force=force, threaded=threaded)


@manager.command
def transcripts(url=None, force=False, threaded=False):
    """ Load all or a specific transcript. """
    _stage(TRANSCRIPT, url=url, force=force, threaded=threaded)


@manager.command
def ablaeufe(url=None, force=False, threaded=False):
    """ Load all or a specific proceeding. """
    _stage(ABLAUF, url=url, force=force, threaded=threaded)


@manager.command
def update(force=False, threaded=False):
    """ Update the entire database. """
    engine = etl_engine()
    indexer = get_indexer()
    try:
        for stage in [GREMIUM, PERSON, ABSTIMMUNG, ABLAUF, TRANSCRIPT]:
            process(engine, indexer, proc, force=force,
                    threaded=threaded)
    finally:
        indexer.flush()


@manager.command
def dumpindex():
    """ Destroy the FTS index. """
    _solr = solr()
    _solr.delete_query("*:*")


@manager.command
def aggregate():
    from offenesparlament.aggregates import make_current_schlagwort, \
        make_period_sachgebiete, make_person_schlagworte
    make_current_schlagwort()
    make_period_sachgebiete()
    make_person_schlagworte()


@manager.command
def notify():
    from offenesparlament.abo import notify
    from offenesparlament.web import app
    notify()


if __name__ == "__main__":
    manager.run()
