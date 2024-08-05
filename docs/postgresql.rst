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


How to Connect to the PostgreSQL Database
=========================================

1. About
--------

In inspire-next stores all the data in a postgresql database.
This document specifies how to connect and query the inspire's PostgreSQL database.
We access it thorught the docker-containers.


2. Run the web container
------------------------

The first step is run the web container, in order to start our database.

.. code-block:: bash

    $ docker compose run --rm web


3. Connect to the PostgresSQL Database
--------------------------------------

When all the containers are up you have to open a new console and run the following command line:

.. code-block:: bash

    $ docker compose exec database psql -U inspirehep

.. code-block:: sql

    psql (9.2.18, server 9.4.5)
    WARNING: psql version 9.2, server version 9.4.
             Some psql features might not work.
    Type "help" for help.

    inspirehep=#


Now you have an interactive console to query the inspire SQL database.
In case PostgreSQL requires the authentication credentials the password for the inspirehep database is `inspirehep`


4. PostgreSQL useful commands
-----------------------------

A list of useful commands:

- ``\h`` this lists all the sql commands that you can run
- ``\dt`` this lists all the tables
- ``\l`` this lists all the databases
- ``\e`` this will open the editor, where you can edit the queries and save it. By doing so the query will get executed.
- ``\?`` this shows the PSQL command prompt help


5. Search a record with the uuid
--------------------------------

Given the uuid of a record you can obtain the record running this query:

.. code-block:: sql

    select * from records_metadata where id = YOUR_UUID;


6. Search a record with the pid
--------------------------------

Given the pid of a record you can obtain the record running this query:

.. code-block:: sql

    select * from pidstore_pid, records_metadata where records_metadata.id = pidstore_pid.object_uuid where pidstore_pid.id = YOUR_PID_ID;
