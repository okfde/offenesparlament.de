DEBUG = True
SECRET_KEY = 'no'
CACHE = True
CACHE_AGE = 84600/2

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/parlament2'
SOLR_URL = 'http://127.0.0.1:8983/solr/parlament'
ETL_URL = 'postgresql://localhost/parlament_etl'
FLATPAGES_ROOT = 'pages'

NOMENKLATURA_PERSONS_DATASET = 'offenesparlament'
NOMENKLATURA_TYPES_DATASET = 'offenesparlament-typen'
NOMENKLATURA_VOTES_DATASET = 'offenesparlament-votes'
NOMENKLATURA_STAGE_DATASET = 'offenesparlament-stand'
NOMENKLATURA_PRELOAD = True

WAHLPERIODEN = [16, 17, 18]
SCRAPE_USER_AGENT = 'OffenesParlament.de // <friedrich@pudo.org>'
SCRAPE_AUTH = ('IOS_APP_v4.2.1', 'RjKtvXnR6EhX8/xqJGRvQcFGDFWoGGTD')
