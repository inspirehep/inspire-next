web: inveniomanage runserver
cache: redis-server
worker: celery worker -E -A invenio_celery.celery --loglevel=DEBUG --workdir=$VIRTUAL_ENV
workermon: flower --broker=amqp://guest:guest@localhost:5672//
indexer: elasticsearch -Dcluster.name="inspire" -Ddiscovery.zen.ping.multicast.enabled=false -Dpath.data="$VIRTUAL_ENV/var/data/elasticsearch"  -Dpath.logs="$VIRTUAL_ENV/var/log/elasticsearch"
