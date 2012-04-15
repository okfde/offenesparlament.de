DEBUG = True
SECRET_KEY = 'no'


#SQLALCHEMY_DATABASE_URI = 'sqlite:///parlament.db'
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/parlament'

# Network = 193.17.224.0/19
# Usable IPs = 193.17.224.1 to 193.17.255.254 for 8190
# Broadcast = 193.17.255.255
# Netmask = 255.255.224.0
# Wildcard Mask = 0.0.31.255

#HTTP_PROXY = 'http://127.0.0.1:3128'

SOLR_URL = 'http://127.0.0.1:8983/solr/parlament'
ETL_URL = 'postgresql://localhost/parlament_etl'
MASTER_URL = 'http://parlament:l4mmm3rt@webstore.openspending.org/parlament/parlamaster'
FLATPAGES_ROOT = 'pages'
