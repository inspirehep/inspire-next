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


Pidstore in Inspire-next
========================

Pidstore is based on on the `Invenio pidstore module
<https://invenio-pidstore.readthedocs.io/en/latest/>`_ that mints,
stores, registers and resolves persistent identifiers. Pidstore has several uses in Inspire-next:

- Map record ids (UUIDs) between ElasticSearch and DataBase. In that way every record, that is stored
  in the Database, can be fetched and imported by ElasticSearch. Also, it's important to notice that
  the records for the front-end are inherited by ``ES Record``, so they are coming from ElasticSearch.

- Pidstore also provide a unique identifier for every record that is the *known* id for the outer world.

In the following you can find how pidstore is connected with Inspire-next.

|

.. image:: images/pidstore_inspire_connection.png
    :height: 390
    :width: 660

|

Pidstore and Database
=====================

There are three basic tables:

- Record Metadata: is the table of the actual record stored in the database. The primary key (id) is
  foreign key (object_uuid) for the table ``Pidstore Pid``. In that way record is mapped to the pidstore.

- Pidstore Pid: is the main table of pidstore in which are stored all the *known* ids called ``pid_value``
  for the outer world. For example given url of a specific record ``https://server_name.cern.ch/literature/1482866`` ,
  number ``1482866`` is the ``pid_value`` stored in ``Pidstore Pid`` table.

- Pidstore Redirect: is the table of pidstore that keeps the mapping of a record that is redirected
  to another record.

|

.. image:: images/Pidstore_DB.png
    :height: 180
    :width: 660

