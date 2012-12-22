from flaskext.script import Manager

from offenesparlament.core import app, etl_engine, solr
from offenesparlament.model.indexer import get_indexer

from offenesparlament.data.persons import process as process_persons, process_person
from offenesparlament.data.gremien import process as process_gremien, process_gremium
from offenesparlament.data.abstimmungen import process as \
    process_abstimmungen, process_abstimmung
from offenesparlament.data.transcripts import process as \
    process_transcripts, process_transcript

manager = Manager(app)


@manager.command
def extract_media():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract import webtv
    webtv.load_sessions(engine)


@manager.command
def extract_docs():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract import dip
    dip.load_dip(engine)

@manager.command
def download_docs():
    """ Download all PDFs from DIP. """
    engine = etl_engine()
    from offenesparlament.extract import documents
    documents.load_documents(engine)

@manager.command
def persons(url=None, force=False):
    """ Load all or a specific person. """
    engine = etl_engine()
    indexer = get_indexer()
    if url is None:
        process_persons(engine, indexer, force=force)
    else:
        process_person(engine, indexer, url,
                       force=force)
    indexer.flush()

@manager.command
def gremien(url=None, force=False):
    """ Load all or a specific committee. """
    engine = etl_engine()
    indexer = get_indexer()
    if url is None:
        process_gremien(engine, indexer, force=force)
    else:
        process_gremium(engine, indexer, url,
                       force=force)
    indexer.flush()

@manager.command
def abstimmungen(url=None, force=False):
    """ Load all or a specific vote. """
    engine = etl_engine()
    indexer = get_indexer()
    if url is None:
        process_abstimmungen(engine, indexer, force=force)
    else:
        process_abstimmung(engine, indexer, url,
                       force=force)
    indexer.flush()

@manager.command
def transcripts(url=None, force=False):
    """ Load all or a specific transcript. """
    engine = etl_engine()
    indexer = get_indexer()
    if url is None:
        process_transcripts(engine, indexer, force=force)
    else:
        process_transcript(engine, indexer, url,
                       force=force)
    indexer.flush()

@manager.command
def update(force=False):
    """ Update the entire database. """
    engine = etl_engine()
    indexer = get_indexer()
    process_gremien(engine, indexer, force=force)
    process_persons(engine, indexer, force=force)
    process_abstimmungen(engine, indexer, force=force)
    indexer.flush()


@manager.command
def transform():
    """ Transform and clean up content """
    engine = etl_engine()
    from offenesparlament.transform import persons
    #persons.generate_person_long_names(engine)
    from offenesparlament.transform import positions
    #positions.extend_positions(engine)
    from offenesparlament.transform import ablaeufe
    #ablaeufe.extend_ablaeufe(engine)
    from offenesparlament.transform import namematch
    namematch.match_persons(engine)
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import speechparser
    speechparser.load_transcripts(engine)
    from offenesparlament.transform import webtv
    webtv.merge_speeches(engine)
    #from offenesparlament.transform import awatch
    #awatch.load_profiles(engine)
    from offenesparlament.transform import speechmatch
    persons.generate_person_long_names(engine)
    speechmatch.extend_speeches(engine)
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import drs
    drs.merge_speeches(engine)

@manager.command
def load():
    """ Load and index staging DB into production """
    engine = etl_engine()
    from offenesparlament.load import load
    load.load(engine)
    load.aggregate()
    from offenesparlament.load import index
    index.index()


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
