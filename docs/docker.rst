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


Docker (Linux)
==============

Docker is an application that makes it simple and easy to run processes in a container,
which are like virtual machines, but more resource-friendly. For a detailed introduction to the different components
of a Docker container, you can follow `this tutorial
<https://www.digitalocean.com/community/tutorials/the-docker-ecosystem-an-introduction-to-common-components>`_.


Inspire and Docker
##################

Get the latest Docker appropriate to your operationg system, by visiting `Docker's official web site <https://www.docker.com/>`_ and accessing the
*Get Docker* section.

.. note:: If you are using Mac, please build a simple box with ``docker-engine`` above ``1.10`` and
         ``docker compose V2``.

Make sure you can run docker without ``sudo``.

- ``id $USER``

  If you are not in the ``docker`` group, run the following command and then restart ``docker``. If this doesn't work, just restart your machine :)

- ``newgrp docker`` or ``su - $USER``

- ``sudo usermod -a -G docker $USER``

Get the latest `docker compose
<https://docs.docker.com/compose/>`_:

.. code-block:: console

   $ sudo pip install docker-compose

- Add ``DOCKER_DATA`` env variable in your ``.bashrc`` or ``.zshrc``. In this directory you will have all the persistent data between Docker runs.

.. code-block:: console

   $ export DOCKER_DATA=~/inspirehep_docker_data/
   $ mkdir -p "$DOCKER_DATA"

By default the virtualenv and everything else will be kept on ``/tmp`` and they will be available only until the next reboot.

- Install a host persistent venv and build assets

.. Note::

 From now on all the docker compose commands must be run at the root of the
 inspire-next repository, you can get a local copy with:

.. code-block:: console

   $ git clone git://github.com/inspirehep/inspire-next
   $ cd inspire-next

.. code-block:: console

   $ docker compose pull
   $ docker compose -f docker-compose.deps.yml run --rm pip

.. note:: If you have trouble with internet connection inside docker probably you are facing known
          DNS issue. Please follow `this solution
          <http://askubuntu.com/questions/475764/docker-io-dns-doesnt-work-its-trying-to-use-8-8-8-8/790778#790778>`_
          with DNS: ``--dns 137.138.17.5 --dns 137.138.16.5``.

.. code-block:: console

   $ docker compose -f docker-compose.deps.yml run --rm assets

- Run the service locally

.. code-block:: console

   $ docker compose up

- Populate database

.. code-block:: console

   $ docker compose run --rm web scripts/recreate_records


Once you have the database populated with the tables and demo records, you can
go to `localhost:5000 <http://localhost:5000>`_


- Run tests in an **isolated** environment.


.. Note::

 The tests use a different set of containers than the default ``docker compose
 up``, so if you run both at the same time you might start having ram/load
 issues, if so, you can stop all the containers started by ``docker compose
 up`` with ``docker compose kill -f``

You can choose one of the following tests types:

  - unit
  - workflows
  - integration
  - integration_async

.. code-block:: console

   $ docker compose -f docker-compose.test.yml run --rm <tests type>
   $ docker compose -f docker-compose.test.yml down

.. tip:: - cleanup all the containers:

           ``docker rm $(docker ps -qa)``

         - cleanup all the images:

           ``docker rmi $(docker images -q)``

         - cleanup the virtualenv (careful, if docker_data is set to something you care about, it will be removed):

           ``sudo rm -rf "${DOCKER_DATA?DOCKER_DATA was not set, ignoring}"``

Extra useful tips
#################

- Run a random shell

.. code-block:: console

   $ docker compose run --rm web inspirehep shell

- Run *virtualenv* bash shell for running scripts manually (e.g. recreating records or `building documentation`_)

.. _building documentation: http://inspirehep.readthedocs.io/en/latest/building_the_docs.html

.. code-block:: console

   $ docker compose run --rm web bash

- Reload code in a worker

.. code-block:: console

   $ docker compose restart worker

- Quick and safe reindex

.. code-block:: console

   $ docker compose restart worker && docker compose run --rm web scripts/recreate_records

- Recreate all static assets. Will download all dependencies from npm and copy all static
  files to ``${DOCKER_DATA}/tmp/virtualenv/var/inspirehep-instance/static``.

.. code-block:: console

   $ docker compose -f docker-compose.deps.yml run --rm assets

- Monitor the output from all the services (elasticsearch, web, celery workers, database, flower, rabbitmq, scrapyd, redis)
  via the following command:

.. code-block:: console

   $ docker compose up
