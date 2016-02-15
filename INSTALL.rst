Installation
============

First install HEPData all requirements:

.. code-block:: console

   $ mkvirtualenv inspirehep
   (inspirehep)$ mkdir src
   (inspirehep)$ git clone https://github.com/inspirehep/inspire-next.git@invenio3#egg=inspirehep
   (inspirehep)$ pip install -r requirements.txt --pre

Next, install and build assets:

.. code-block:: console

   (inspirehep)$ npm update && npm install -g node-sass clean-css requirejs uglify-js
   (inspirehep)$ inspirehep npm
   (inspirehep)$ cdvirtualenv var/inspirehep-instance/static
   (inspirehep)$ npm install
   (inspirehep)$ inspirehep collect -v
   (inspirehep)$ inspirehep assets build


Next, create the database and database tables if you haven't already done so:

.. code-block:: console

   (inspirehep)$ psql
   # CREATE USER inspirehep WITH PASSWORD 'dbpass123';
   # CREATE DATABASE inspirehep;
   # GRANT ALL PRIVILEGES ON DATABASE inspirehep to inspirehep;
   (inspirehep)$ inspirehep db init
   (inspirehep)$ inspirehep db create


Optionally, create the initial user:

.. code-block:: console

   (inspirehep)$ inspirehep users create your@email.com -a


Run Celery

.. code-block:: console

   (inspirehep)$ celery worker -E -A inspirehep.celery


Now, start inspirehep:

.. code-block:: console

   (inspirehep)$ inspirehep --debug run
