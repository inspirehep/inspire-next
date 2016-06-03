============
Installation
============

Create a virtual environment
============================

Create a virtual environment and clone the INSPIRE source code using `git`:

.. code-block:: console

    $ mkvirtualenv inspirehep
    $ workon inspirehep
    (inspirehep)$ cdvirtualenv
    (inspirehep)$ mkdir src
    (inspirehep)$ git clone https://github.com/inspirehep/inspire-next.git inspirehep


Install requirements
====================

Use `pip` to install all requirements:

.. code-block:: console

    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ pip install -r requirements.txt --pre --exists-action i


Build assets
============

We build assets using `npm`. Make sure you have installed it system wide.

.. code-block:: console

    (inspirehep)$ npm update && npm install -g node-sass clean-css requirejs uglify-js


Then we build the INSPIRE assets:

.. code-block:: console

    (inspirehep)$ inspirehep npm
    (inspirehep)$ cdvirtualenv var/inspirehep-instance/static
    (inspirehep)$ npm install
    (inspirehep)$ inspirehep collect -v
    (inspirehep)$ inspirehep assets build


.. note::

    Alternatively, run `sh scripts/clean_assets` to do the above in one command.


Create database
===============

We will use `postgreSQL` as database. Make sure you have installed it system wide.

Then create the database and database tables if you haven't already done so:

.. code-block:: console

    (inspirehep)$ psql
    # CREATE USER inspirehep WITH PASSWORD 'dbpass123';
    # CREATE DATABASE inspirehep;
    # GRANT ALL PRIVILEGES ON DATABASE inspirehep to inspirehep;
    (inspirehep)$ inspirehep db init
    (inspirehep)$ inspirehep db create


Create user
===========

Next, create the initial user who will become superadmin:

.. code-block:: console

    (inspirehep)$ inspirehep users create your@email.com -a


Start all services
==================

We use `honcho` to manage our services and run the development server. See `Procfile` for details.

.. code-block:: console

    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ honcho start


And the site is now available on `http://localhost:5000`.


Create ElasticSearch Indices and Aliases
========================================

We will use `elasticsearch` as search engine. Make sure you have installed it system wide.

.. code-block:: console

    (inspirehep)$ inspirehep index init


.. note::

    You have to install the `analysis-icu` elasticsearch plugin for this command to work.

    .. code-block:: console

        plugin install elasticsearch/elasticsearch-analysis-icu/X.X.X

    See here to find the right version for your elasticsearch installation
    https://github.com/elastic/elasticsearch-analysis-icu#icu-analysis-for-elasticsearch


If you are having troubles creating your indices, e.g. due to index name changes or existing legacy indices, try:


.. code-block:: console

    (inspirehep)$ inspirehep index destroy --force --yes-i-know
    (inspirehep)$ inspirehep index init


Add demo records
================

.. code-block:: console

    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ inspirehep migrator populate -f inspirehep/demosite/data/demo-records.xml.gz


.. note::

    Alternatively, run `sh scripts/recreate_records` to drop db/index/records and re-create them in one command.


.. warning::

    Remember to keep `honcho` running in a separate window.


Adding records from files
=========================

Same way as demo records:

.. code-block:: console

    (inspirehep)$ inspirehep migrator populate -f inspirehep/demosite/data/sample.xml



Access the records (web/rest)
=============================

While running `honcho` you can access the records at

.. code-block:: console

    firefox http://localhost:5000/literature/1
    curl -i -H "Accept: application/json" http://localhost:5000/api/records/1



Generating doJSON output
========================

If you want to test the doJSON output for a specific rule, make sure it is added to doJSON
entry points and then do the following (e.g. for the `hep` rule):

.. code-block:: console

    dojson -l marcxml -i inspirehep/demosite/data/sample.xml do hep
