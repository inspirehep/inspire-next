Installation
============

First install HEPData all requirements:

.. code-block:: console

   $ mkvirtualenv inspirehep
   (inspirehep)$ mkdir src
   (inspirehep)$ git clone -b invenio3 https://github.com/inspirehep/inspire-next.git
   (inspirehep)$ pip install -r requirements.txt --pre

Next, install and build assets:

.. code-block:: console

   (inspirehep)$ npm update && npm install -g node-sass clean-css requirejs uglify-js
   (inspirehep)$ inspirehep npm
   (inspirehep)$ cdvirtualenv var/inspirehep-instance/static
   (inspirehep)$ npm install
   (inspirehep)$ inspirehep collect -v
   (inspirehep)$ inspirehep assets build   # NOTE: Might give an error about missing `minjs`, pip install it to fix.


Next, create the database and database tables if you haven't already done so:

.. code-block:: console

   (inspirehep)$ psql
   # CREATE USER inspirehep WITH PASSWORD 'dbpass123';
   # CREATE DATABASE inspirehep;
   # GRANT ALL PRIVILEGES ON DATABASE inspirehep to inspirehep;
   (inspirehep)$ inspirehep db init
   (inspirehep)$ inspirehep db create


Usage
=====

Optionally, create the initial user:

.. code-block:: console

   (inspirehep)$ inspirehep users create your@email.com -a

Optionally, add a record:

.. code-block:: console

   (inspirehep)$ demouuid = $(dojson do -l marcxml -i inspirehep/demosite/data/sample.xml hep | inspirehep records create)
   (inspirehep)$ inspirehep pid create -t rec -i $demouuid -s REGISTERED recid 1


Run Celery

.. code-block:: console

   (inspirehep)$ celery worker -E -A inspirehep.celery


Now, start inspirehep:

.. code-block:: console

   (inspirehep)$ inspirehep --debug run


Access the record (web/rest):

.. code-block:: console

   firefox http://localhost:5000/records/1
   curl -i -H "Accept: application/json" http://localhost:5000/api/records/1


Search
======

.. code-block:: console

   (inspirehep)$ inspirehep index init
