============
Installation
============

First install all requirements:

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


Next, create the ElasticSearch Indices and Aliases (this should be done before database init for collection percolators to work):

.. code-block:: console

   (inspirehep)$ inspirehep index init

**NOTE:** you have to install the analysis-icu plugin for this command to work.

Next, create the database and database tables:

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


Start honcho
~~~~~~~~~~~~

.. code-block:: console

   (inspirehep)$ honcho start

And the site is now available on `http://localhost:5000`.

**PS: Note the new port!**


Add demo records
~~~~~~~~~~~~~~~~

.. code-block:: console

   (inspirehep)$ inspirehep migrator populate -f inspirehep/demosite/data/demo-records.xml.gz


Adding a single record with CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   (inspirehep)$ demouuid = $(dojson do -l marcxml -i inspirehep/demosite/data/sample.xml hep | inspirehep records create)
   (inspirehep)$ inspirehep pid create -t rec -i $demouuid -s REGISTERED recid 1


Access the record (web/rest)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   firefox http://localhost:5000/records/1
   curl -i -H "Accept: application/json" http://localhost:5000/api/records/1


======
ENJOY!
======
