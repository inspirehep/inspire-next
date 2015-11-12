#!/usr/bin/env bash

# Run services
service mysql start
service redis-server start
service rabbitmq-server start
/elasticsearch-"${ES_VERSION}"/bin/elasticsearch --path.plugins="/elasticsearch-${ES_VERSION}/plugins" 1> /dev/null &

# Needed to fix Python 2.7.9 TypeError with Jinja2.
# See: https://github.com/inveniosoftware/invenio/issues/2862#issuecomment-90508434
pip install unittest2

# Install INSPIRE
pip install -r requirements.txt --quiet

# Configuration
inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.console.Mail
inveniomanage config set CFG_BIBSCHED_PROCESS_USER `whoami`
inveniomanage config set PACKAGES_EXCLUDE []  # test all packages
inveniomanage config set CFG_TMPDIR /tmp
inveniomanage config set CFG_SITE_URL http://localhost
inveniomanage config set CFG_SITE_SECURE_URL https://localhost
inveniomanage config set ASSETS_DEBUG True  # ignore assets issues
inveniomanage config set LESS_RUN_IN_DEBUG False
inveniomanage config set REQUIREJS_RUN_IN_DEBUG False

inveniomanage bower -i bower-base.json > bower.json
bower install --silent --force-latest --allow-root

inveniomanage config set COLLECT_STORAGE flask.ext.collect.storage.link
inveniomanage collect > /dev/null
inveniomanage assets build
inveniomanage config set CLEANCSS_BIN false  # deactivate all the things
inveniomanage config set LESS_BIN false      # false is /usr/bin/false
inveniomanage config set REQUIREJS_BIN false
inveniomanage config set UGLIFYJS_BIN false
inveniomanage config set ASSETS_AUTO_BUILD False

# Database configuration
inveniomanage database init --user=root --password= --yes-i-know || echo ':('
inveniomanage database create --quiet || echo ':('

# Start Celery
celery worker -E -A invenio_celery.celery --workdir=$VIRTUAL_ENV 1> /dev/null &

# Load demo records
inveniomanage migrator populate -t marcxml -f `pwd`/inspire/demosite/data/demo-records.xml --force
