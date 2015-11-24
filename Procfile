web: sleep 10 && inveniomanage runserver
cache: sleep 10 && redis-server
worker: sleep 10 && celery worker -E -A invenio_celery.celery --loglevel=INFO --workdir=$VIRTUAL_ENV
workermon: sleep 10 && flower --broker=amqp://guest:guest@localhost:5672//
indexer: elasticsearch --config=elasticsearch.yml --path.data="$VIRTUAL_ENV/var/data/elasticsearch"  --path.logs="$VIRTUAL_ENV/var/log/elasticsearch"
