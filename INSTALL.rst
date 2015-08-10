Installation
=============

1. About
--------

This document specifies how to install a development version of Inspire for the
first time. Production grade deployment is not covered here.


2. Prerequisites
----------------

To install the overlay, first follow the "2. Prerequisites" in `First Steps with Invenio <http://invenio.readthedocs.org/en/latest/getting-started/first-steps.html#prerequisites>`_.

Come back to this documentation to continue the installation.

Inspire uses RabbitMQ as it's default message broker, so you need to make sure
you have a RabbitMQ server installed and running:

.. code-block:: console

    $ sudo apt-get install rabbitmq-server


Or, on MAC:

.. code-block:: console

    $ brew install rabbitmq

This overlay replaces the `invenio-demosite` so all references to such demosite should be ignored and executed in this overlay instead.


3. Quick start
--------------

3.1. Getting the source code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First go to GitHub and fork both Invenio and Inspire repositories if you have
not already done so (see Step 1 in
`Fork a Repo <https://help.github.com/articles/fork-a-repo>`_):

- `Invenio <https://github.com/inveniosoftware/invenio>`_
- `Inspire <https://github.com/inspirehep/inspire-next>`_

Next, clone your forks to get development versions of Invenio and Inspire.

.. code-block:: console

    $ cd $HOME/src/
    $ git clone https://github.com/<username>/invenio.git
    $ git clone https://github.com/<username>/inspire-next.git

Make sure you configure upstream remote for the repository so you can fetch
updates to the repository.

.. code-block:: console

    $ cd $HOME/src/invenio
    $ git remote add upstream https://github.com/inveniosoftware/invenio.git
    $ git fetch upstream
    $ cd $HOME/src/inspire-next
    $ git remote add inspire https://github.com/inspirehep/inspire-next.git
    $ git fetch inspire


Note that Inspire uses a forked version of Invenio with some special customizations, so you should make sure to also get the Inspire flavour of Invenio:

.. code-block:: console

    $ cd $HOME/src/invenio
    $ git remote add inspire https://github.com/inspirehep/invenio.git
    $ git fetch inspire


3.2 Working environment
~~~~~~~~~~~~~~~~~~~~~~~

We recommend to work using
`virtual environments <http://www.virtualenv.org/>`_ so packages are installed
in an isolated environment . ``(inspire)$`` tells that your
*inspire* environment is the active one.

.. code-block:: console

    $ mkvirtualenv inspire
    (inspire)$ # we are in the inspire environment now and
    (inspire)$ # can leave it using the deactivate command.
    (inspire)$ deactivate
    $ # Now join it back, recreating it would fail.
    $ workon inspire
    (inspire)$ # That's all there is to know about it.

Let's create a working copy of the Invenio and Inspire source code in the
just created environment.

.. code-block:: console

    (inspire)$ cdvirtualenv
    (inspire)$ mkdir src; cd src
    (inspire)$ git-new-workdir $HOME/src/invenio/ invenio labs
    (inspire)$ git-new-workdir $HOME/src/inspire-next/ inspire-next master


.. NOTE::
    By default we checkout the development branches ``master`` for Inspire
    overlay and ``labs`` for Invenio.


3.3 Installation
~~~~~~~~~~~~~~~~
The steps for installing Inspire are nearly identical to a normal Invenio
installation. First install Invenio sources:

.. code-block:: console

    (inspire)$ cdvirtualenv src/invenio
    (inspire)$ pip install --process-dependency-links -e .[development]
    (inspire)$ python setup.py compile_catalog


Then proceed to install the Inspire overlay:

.. code-block:: console

    (inspire)$ cdvirtualenv src/inspire-next
    (inspire)$ pip install -r requirements.txt --exists-action i

.. NOTE::
   The option ``--exists-action i`` for ``pip install`` is needed to ensure
   that the Invenio source code we just cloned will not be overwritten. If you
   omit it, you will be prompted about which action to take.

For development environments you should install our git commit hooks that
checks code according to our code quality standards:

.. code-block:: console

    (inspire)$ cd $HOME/src/invenio/
    (inspire)$ kwalitee githooks install
    (inspire)$ cd $HOME/src/inspire-next/
    (inspire)$ kwalitee githooks install


3.4. Configuration
~~~~~~~~~~~~~~~~~~

Generate the secret key for your installation.

.. code-block:: console

    (inspire)$ inveniomanage config create secret-key
    (inspire)$ inveniomanage config set CFG_EMAIL_BACKEND flask_email.backends.console.Mail
    (inspire)$ inveniomanage config set CFG_BIBSCHED_PROCESS_USER $USER
    (inspire)$ inveniomanage config set CFG_DATABASE_NAME inspire
    (inspire)$ inveniomanage config set CFG_DATABASE_USER inspire
    (inspire)$ inveniomanage config set CFG_SITE_URL http://localhost:4000
    (inspire)$ inveniomanage config set CFG_SITE_SECURE_URL http://localhost:4000
    (inspire)$ inveniomanage config set COLLECT_STORAGE flask_collect.storage.link


.. NOTE::
   Make sure to name your database in lowercase without any special characters.


When developing on top of INSPIRE and Invenio, we recommend setting the
following Invenio config variables:

.. code-block:: bash

    (inspire)$ inveniomanage config set DEBUG True
    (inspire)$ inveniomanage config set ASSETS_DEBUG True


3.5. Assets
~~~~~~~~~~~

Installing the required assets (JavaScript, CSS, etc.) via bower. The file
``.bowerrc`` is configuring where bower will download the files and
``bower.json`` what libraries to download.

.. code-block:: console

    (inspire)$ cdvirtualenv src/inspire-next
    (inspire)$ inveniomanage bower -i bower-base.json > bower.json
    Generates or update bower.json for you.
    (inspire)$ cat .bowerrc
    {
        "directory": "inspire/base/static/vendors"
    }
    (inspire)$ bower install
    (inspire)$ ls inspire/base/static/vendors
    bootstrap
    ckeditor
    hogan
    jquery
    jquery-tokeninput
    jquery-ui
    plupload
    ...


Assets in non-development mode may be combined and minified using various
filters. We need to set the path to the binaries if
they are not in the environment ``$PATH`` already.

.. code-block:: console

    # Local installation (using package.json)
    (invenio)$ cdvirtualenv src/invenio
    (invenio)$ npm install
    (invenio)$ inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
    (invenio)$ inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`
    (invenio)$ inveniomanage config set REQUIREJS_BIN `find $PWD/node_modules -iname r.js | head -1`
    (invenio)$ inveniomanage config set UGLIFYJS_BIN `find $PWD/node_modules -iname uglifyjs | head -1`

All the assets that are spread among every invenio module or external libraries
will be collected into the instance directory. By default, it create copies of
the original files. As a developer you may want to have symbolic links instead.

.. code-block:: console

    (invenio)$ inveniomanage collect
    ...
    Done collecting.
    (invenio)$ cdvirtualenv var/invenio.base-instance/static
    (invenio)$ ls -l
    css
    js
    vendors
    ...


3.6. Demosite
~~~~~~~~~~~~~

Once you have everything installed, you can create the database and populate it
with demo records.

.. code-block:: console

    (invenio)$ inveniomanage database init --user=root --password=$MYSQL_ROOT --yes-i-know
    (invenio)$ inveniomanage database create


As a developer, you may want to use the provided
``Procfile`` with `honcho <https://pypi.python.org/pypi/honcho>`_. It
starts all the services at once with nice colors. By default, it also runs
`flower <https://pypi.python.org/pypi/flower>`_ which offers a web interface
to monitor the *Celery* tasks.

.. code-block:: console

    (invenio)$ pip install honcho flower
    (invenio)$ cdvirtualenv src/inspire-next
    (invenio)$ honcho start

You can now load the INSPIRE demo records:

.. code-block:: console

    (inspire)$ cdvirtualenv src/inspire-next
    (inspire)$ inveniomanage records create inspire/demosite/data/demo-records.xml -t marcxml


Now you should have a running INSPIRE demo site running at `http://localhost:4000 <http://localhost:4000>`_!


3.6. Addendum
~~~~~~~~~~~~~

You can also start a server without using honcho with the `runserver` command:

.. code-block:: console

    (inspire)$ inveniomanage runserver

You can go to a shell instance with database initialized using the `shell` command:

.. code-block:: console

    (inspire)$ inveniomanage shell
    In [1]: app
    Out[1]: <Flask 'invenio.base'>


4. Harvesting workflows
-----------------------

4.1 CORE prediction
~~~~~~~~~~~~~~~~~~~

If you need to setup prediction models such as the CORE guessing it is required to install some extra packages such as beard which requires scipy, numpy and scikit-learn. This means that you need to make sure you have the required libraries installed.

For example, on Ubuntu/Debian you could execute:

.. code-block:: bash

    (inspire)$ sudo aptitude install -y libblas-dev liblapack-dev gfortran imagemagick

Then to install beard:

.. code-block:: bash

    (inspire)$ cdvirtualenv src/inspire-next
    (inspire)$ pip install -r requirements-harvesting.txt --exists-action i


Now you can train a prediction model or use an existing pickled model file:

.. code-block:: bash

    (inspire)$ cdvirtualenv var/data/classifier/models/
    (inspire)$ cp /path/to/core_guessing.pickle .

Here is how to train the model from scratch:

.. code-block:: bash

    (inspire)$ inveniomanage classifier train -r /path/to/trainingset.json -o core_guessing.pickle


TODO: Add link to training set.
TODO: Add link sample model.

5. Known issues
---------------

5.1 Problem with invenio-query-parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On a fresh install in a new virtual environment you may experience that search
queries are failing due to query parser issues. It means that an older version
of invenio-query-parser is installed. You can fix it by installing the lastest
sources:

.. code-block:: bash

    (inspire)$ pip install --upgrade git+https://github.com/inveniosoftware/invenio-query-parser@master#egg=invenio-query-parser

