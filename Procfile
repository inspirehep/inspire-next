web: inveniomanage runserver
cache: redis-server
worker: celery worker -E -A invenio.celery.celery --loglevel=INFO --workdir=$VIRTUAL_ENV
#workermon: flower --broker=amqp://guest:guest@localhost:5672//
indexer: elasticsearch --config=~/Desktop/elasticsearch-1.7.1/config/elasticsearch.yml
