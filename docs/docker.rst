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


====================
2.1.5.1 About Docker
====================

Docker is an application that makes it simple and easy to run application processes in a container,
which are like virtual machines, only more portable, more resource-friendly, and more dependent
on the host operating system. For a detailed introduction to the different components of a Docker
container.

Useful `Tutorial
<https://www.digitalocean.com/community/tutorials/the-docker-ecosystem-an-introduction-to-common-components>`_.

==========================
2.1.5.2 Inspire and Docker
==========================

Get the latest Docker setup.

- If you are using Mac, please build a simple box with ``docker-engine`` above ``1.10`` and ``docker-compose`` above ``1.6.0``.

Make sure you can run docker without ``sudo``.

- ``id $USER``

  If you are not in the ``docker`` group, run the following command and then restart ``docker``. If this doesn't work, just restart your machine :)
-  ``sudo usermod -a -G docker $USER``

Get docker-compose:

.. code-block:: console

 sudo pip install docker-compose

- Add ``DOCKER_DATA`` env variable in your ``.bashrc`` or ``.zshrc``. In this directory you will have all the persistent data between Docker runs.

.. code-block:: console

 export DOCKER_DATA=~/inspirehep_docker_data/

By default the virtualenv and everything else will be kept on ``/tmp`` and they will be available only until the next reboot.

- Install a host persistent venv and build assets

.. code-block:: console

 docker-compose pull
 docker-compose -f docker-compose.deps.yml run --rm pip
 docker-compose -f docker-compose.deps.yml run --rm assets

- Run the service locally

.. code-block:: console

 docker-compose up

Go to ``localhost:5000``

- Populate database

.. code-block:: console

 docker-compose run --rm web scripts/recreate_records

- Run tests in an **isolated** environment:

.. code-block:: console

 docker-compose -f docker-compose.test.yml run --rm test
 docker-compose -f docker-compose.test.yml kill
 docker-compose -f docker-compose.test.yml rm

**The kill command is mandatory, otherwise you will use the test DB instead of the correct one in dev.**

I don't know how to kill all the other services just after the run command exited.


=========================
2.1.5.3 Extra useful tips
=========================

- Run a random shell

After ``docker-compose up`` just run:

.. code-block:: console

 docker-compose run --rm web inspirehep shell

- Reload code in a worker

With ``docker-compose up`` just run:

.. code-block:: console

 docker-compose restart worker

- Quick and safe reindex

With ``docker-compose up`` just run:

.. code-block:: console

 docker-compose restart worker && docker-compose run --rm web scripts/recreate_records
