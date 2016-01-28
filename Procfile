web: inveniomanage runserver
cache: redis-server
worker: celery worker -E -A invenio_celery.celery --loglevel=INFO --workdir=$VIRTUAL_ENV
workermon: celery flower -A invenio_celery.celery
indexer: elasticsearch -Dcluster.name="inspire" -Ddiscovery.zen.ping.multicast.enabled=false -Dpath.data="$VIRTUAL_ENV/var/data/elasticsearch"  -Dpath.logs="$VIRTUAL_ENV/var/log/elasticsearch"
