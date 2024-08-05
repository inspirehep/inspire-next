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

CentOS
~~~~~~

.. code-block:: console

    $ sudo yum install python-virtualenv python-virtualenvwrapper \
        npm postgresql postgresql-devel libxml2-devel ImageMagick redis git \
        libxslt-devel
    $ sudo npm -g install npm

For elasticsearch you can find the installation instructions on the
`elasticsearch install page`_, and, to run the development environment, you
will need also to add the following workarounds:

.. code-block:: console

    $ sudo usermod -a -G $USER elasticsearch
    $ newgrp elasticsearch  # or log out and in again
    $ sudo ln -s /etc/elasticsearch /usr/share/elasticsearch/config

MacOS
~~~~~

.. code-block:: console

    $ brew install libxml2
    $ brew install libxslt
    $ brew cask install caskroom/versions/java8
    $ brew install imagemagick@6
    $ brew install libmagic
    $ brew install ghostscript
    $ brew install poppler

You might also need to link imagemagick:

.. code-block:: console

    $ brew link --force imagemagick@6

Add to ~/.bash_profile:

.. code-block:: console

    # ElasticSearch.
    export PATH="/usr/local/opt/elasticsearch@2.4/bin:$PATH"


Create a virtual environment
############################

Create a virtual environment and clone the INSPIRE source code using `git`:

.. code-block:: console

    $ mkvirtualenv --python=python2.7 inspirehep
    $ workon inspirehep
    (inspirehep)$ cdvirtualenv
    (inspirehep)$ mkdir src
    (inspirehep)$ git clone https://github.com/inspirehep/inspire-next.git src/inspirehep

.. note::

    It is also possible (and more flexible) to do the above the other way
    around like this and clone the project into a folder of your choice:

    .. code-block:: console

        $ git clone https://github.com/inspirehep/inspire-next.git inspirehep
        $ cd inspirehep
        $ mkvirtualenv --python=python2.7 inspirehep
        $ workon inspirehep

    This approach enables you to switch to a new virtual environment
    without having to clone the project again. You simply specify on
    which environment you want to ``workon`` using its name.

    Just be careful to replace all ``cdvirtualenv src/inspirehep`` in the
    following with a ``cd path_you_chose/inspirehep``.

Install requirements
####################

Use `pip` to install all requirements, it's recommended to upgrade pip and
setuptools to latest too:

.. code-block:: console

    (inspirehep)$ pip install --upgrade pip setuptools
    (inspirehep)$ cdvirtualenv src/inspirehep
    (inspirehep)$ pip install -r requirements.txt --pre --exists-action i
    (inspirehep)$ pip install honcho

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

    In particular, if you want to install the ``npm`` packages directly in your
    ``virtualenv``, just add ``NPM_CONFIG_PREFIX=$VIRTUAL_ENV`` in the
    ``postactivate`` file of your ``virtualenv`` folder and you will be able to
    run the above command from inside your virtual environment.


Then we build the INSPIRE assets:

.. code-block:: console

    (inspirehep)$ inspirehep npm
    (inspirehep)$ cdvirtualenv var/inspirehep-instance/static
    (inspirehep)$ npm install
    (inspirehep)$ inspirehep collect -v
    (inspirehep)$ inspirehep assets build


.. note::

    Alternatively, run `sh scripts/clean_assets` to do the above in one command.

Start all services
##################

We will start, postgresql, elasticsearch, redis and rabbitmq.

Then create the database and database tables if you haven't already done so:

.. code-block:: console

    (inspirehep)$ docker compose up database indexer redis rabbitmq


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
    (inspirehep)$ inspirehep migrate file --force --wait inspirehep/demosite/data/demo-records.xml.gz


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
