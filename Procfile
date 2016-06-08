web: gunicorn inspirehep.wsgi -c gunicorn.cfg
cache: redis-server
worker: celery worker -E -A inspirehep.celery --loglevel=INFO --workdir="${VIRTUAL_ENV}" --autoreload --pidfile="${VIRTUAL_ENV}/worker.pid" --purge
workermon: flower --broker=amqp://guest:guest@localhost:5672//
# mathoid: node_modules/mathoid/server.js -c mathoid.config.yaml
indexer: elasticsearch -Dcluster.name="inspire" -Ddiscovery.zen.ping.multicast.enabled=false -Dpath.data="$VIRTUAL_ENV/var/data/elasticsearch"  -Dpath.logs="$VIRTUAL_ENV/var/log/elasticsearch"
