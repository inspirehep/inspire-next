web: inveniomanage runserver
cache: redis-server
worker: celery worker -E -A invenio.celery.celery --loglevel=INFO --workdir=$VIRTUAL_ENV
workermon: flower --broker=amqp://guest:guest@localhost:5672//
indexer: elasticsearch --config=elasticsearch.yml --path.data="$VIRTUAL_ENV/var/data/elasticsearch"  --path.logs="$VIRTUAL_ENV/var/log/elasticsearch"
