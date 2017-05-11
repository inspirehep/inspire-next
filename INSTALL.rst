..
    This file is part of INSPIRE.
    Copyright (C) 2017 CERN.

    INSPIRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    INSPIRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.

    In applying this licence, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.


Native Install (CentOS - MacOS)
===============================

System prerequisites
####################

This guide expects you to have installed in your system the following tools:

* pip
* git
* virtualenv
* virtualenvwrapper
* npm > 3.0
* postgresql + devel headers
* libxml2 + devel headers
* libxslt + devel headers
* ImageMagick
* redis
* elasticsearch

.. code-block:: console

    $ sudo yum install python-pip python-virtualenv python-virtualenvwrapper \
        npm postgresql postgresql-devel libxml2-devel ImageMagick redis git \
        libxslt-devel
    $ sudo npm -g install npm

For elasticsearch you can find the installation instructions on the
`elasticsearch install page`_, and, to run the development environment, you
will need also add the following workarounds:

.. code-block:: console

    $ sudo usermod -a -G $USER elasticsearch
    $ newgrp elasticsearch  # or log out and in again
    $ sudo ln -s /etc/elasticsearch /usr/share/elasticsearch/config

Create a virtual environment
############################

Create a virtual environment and clone the INSPIRE source code using `git`:

.. code-block:: console

    $ mkvirtualenv inspirehep
    $ workon inspirehep
    (inspirehep)$ cdvirtualenv
    (inspirehep)$ mkdir src
    (inspirehep)$ git clone https://github.com/inspirehep/inspire-next.git src/inspirehep

Install requirements
####################

Use `pip` to install all requirements, it's recommended to upgrade pip and
setuptools to latest too:

.. code-block:: console

    (inspirehep)$ pip install --upgrade pip setuptools
    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ pip install -r requirements.txt --pre --exists-action i

And for development:

.. code-block:: console

    (inspirehep)$ pip install -e .[development]

Custom configuration and debug mode
###################################

If you want to change the database url, or enable the debug mode for
troubleshooting, you can do so in the `inspirehep.cfg` file under
`var/inspirehep-instance`, you might need to create it:

.. code-block:: console

    (inspirehep)$ cdvirtualenv var/inspirehep-instance
    (inspirehep)$ vim inspirehep.cfg


There you can change the value of any of the variables that are set under the
file `src/inspirehep/inspirehep/config.py`, for example:


.. code-block:: python

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://someuser:somepass@my.postgres.server:5432/inspirehep"


.. note::

    Make sure that the configuration keys you override here have the same exact
    name as the ones in the config.py file, as it will not complain if you put
    a key that did not exist.


Build assets
############

We build assets using `npm`. Make sure you have installed it system wide.

.. code-block:: console

    (inspirehep)$ sudo npm update
    (inspirehep)$ sudo npm install -g node-sass@3.8.0 clean-css@^3.4.24 requirejs uglify-js


.. note::

    If you don't want to use sudo to install the npm packages globally, you can
    still setup a per-user npm modules installation that will allow you to
    install/remove modules as normal user. You can find more info `in the npm
    docs here`_.


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
###############

We will use `postgreSQL` as database. Make sure you have installed it system wide.

Then create the database and database tables if you haven't already done so:

.. code-block:: console

    (inspirehep)$ psql
    # CREATE USER inspirehep WITH PASSWORD 'dbpass123';
    # CREATE DATABASE inspirehep;
    # GRANT ALL PRIVILEGES ON DATABASE inspirehep to inspirehep;
    (inspirehep)$ inspirehep db init
    (inspirehep)$ inspirehep db create

Start all services
##################

Rabbitmq
~~~~~~~~

You must have rabbitmq installed and running (and reachable) somewhere.
To run it locally on a CentOS:

.. code-block:: console

    $ sudo yum install rabbitmq-server
    $ sudo service rabbitmq-server start
    $ sudo systemctl enable rabbitmq-server.service  # to start on system boot

Everything else: Honcho
~~~~~~~~~~~~~~~~~~~~~~~

We use `honcho`_ to manage our services and run the development server. See
`Procfile`_ for details.

.. code-block:: console

    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ honcho start


And the site is now available on http://localhost:5000.

Create ElasticSearch Indices and Aliases
########################################

.. note::

    Remember that you'll need to have the elasticsearch bin directory in your
    $PATH or prepend the binaries executed with the path to the elasticsearch
    bin directory in your system.

First of all, we will need to install the `analysis-icu` elasticsearch plugin.

.. code-block:: console

    (inspirehep)$ plugin install analysis-icu


Now we are ready to create the indexes:

.. code-block:: console

    (inspirehep)$ inspirehep index init


If you are having troubles creating your indices, e.g. due to index name
changes or existing legacy indices, try:


.. code-block:: console

    (inspirehep)$ inspirehep index destroy --force --yes-i-know
    (inspirehep)$ inspirehep index init

Create admin user
#################

Now you can create a sample admin user, for that we will use the fixtures:

.. code-block:: console

    (inspirehep)$ inspirehep fixtures init

.. note::

    If you are not running in debug mode, remember to add the `local=1` HTTP
    GET parameter to the login url so it will show you the login form, for
    example:

        http://localhost:5000/login/?local=1

Add demo records
################

.. code-block:: console

    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ inspirehep migrator populate -f inspirehep/demosite/data/demo-records.xml.gz --wait=true


.. note::

    Alternatively, run `sh scripts/recreate_records` to drop db/index/records
    and re-create them in one command, it will also create the admin user.


.. warning::

    Remember to keep `honcho` running in a separate window.

Create regular user
###################

Now you can create regular users (optional) with the command:

.. code-block:: console

    (inspirehep)$ inspirehep users create your@email.com -a

Adding records from files
#########################

Same way as demo records:

.. code-block:: console

    (inspirehep)$ inspirehep migrator populate -f inspirehep/demosite/data/sample.xml


Access the records (web/rest)
#############################

While running `honcho` you can access the records at

.. code-block:: console

    $ firefox http://localhost:5000/literature/1
    $ curl -i -H "Accept: application/json" http://localhost:5000/api/records/1


Generating doJSON output
########################

If you want to test the doJSON output for a specific rule, make sure it is added to doJSON
entry points and then do the following (e.g. for the `hep` rule):

.. code-block:: console

    (inspirehep)$ dojson -l marcxml -i inspirehep/demosite/data/sample.xml do hep


.. _this issue: https://github.com/inspirehep/inspire-next/issues/1296
.. _elasticsearch install page: https://www.elastic.co/downloads/elasticsearch
.. _in the npm docs here: https://docs.npmjs.com/getting-started/fixing-npm-permissions#option-2-change-npms-default-directory-to-another-directory
.. _honcho: https://honcho.readthedocs.io/en/latest/
.. _Procfile: https://devcenter.heroku.com/articles/procfile
