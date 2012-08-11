from flaskext.script import Manager
from webstore.client import URL as WebStore

from offenesparlament.core import app, master_data, etl_engine

manager = Manager(app)


@manager.command
def extract_base():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract.xml import ausschuss
    ausschuss.load_index(engine)
    from offenesparlament.extract.xml import news
    #news.load_index(engine)
    from offenesparlament.extract.xml import mdb
    mdb.load_index(engine)


@manager.command
def extract_votes():
    """ Run the extract stage """
    engine = etl_engine()
    from offenesparlament.extract import abstimmungen
    abstimmungen.load_index(engine)


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
def transform():
    """ Transform and clean up content """
    engine = etl_engine()
    from offenesparlament.transform import persons
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import positions
    positions.extend_positions(engine)
    from offenesparlament.transform import namematch
    namematch.match_persons(engine)
    from offenesparlament.transform import abstimmungen
    abstimmungen.extend_abstimmungen(engine)
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import speechparser
    speechparser.load_transcripts(engine)
    from offenesparlament.transform import webtv
    webtv.merge_speeches(engine)
    from offenesparlament.transform import awatch
    awatch.load_profiles(engine)
    from offenesparlament.transform import speechmatch
    persons.generate_person_long_names(engine)
    speechmatch.extend_speeches(engine)
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import drs
    drs.merge_speeches(engine)

@manager.command
def devtf():
    """ Transform and clean up content (dev bits) """
    engine = etl_engine()
    from offenesparlament.transform import drs
    drs.merge(engine)

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
def index():
    """ Rebuild the FTS index. """
    #engine = etl_engine()
    from offenesparlament.load import index
    index.index()


@manager.command
def longextract():
    """ Run the extract stage, including long-running tasks """
    engine = etl_engine()
    from offenesparlament.extract import wahlkreise
    wahlkreise.load_wahlkreise(engine)


@manager.command
def notify():
    from offenesparlament.abo import notify
    from offenesparlament.web import app
    notify()

if __name__ == "__main__":
    manager.run()
