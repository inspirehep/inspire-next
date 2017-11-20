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


Alembic
************

Create an alembic revision
=======================

We use `alembic <https://invenio-db.readthedocs.io/en/latest/alembic.html>`_ as a migration tool integrated in `invenio-db`.
If you want to create a new alembic revision in INSPIRE you should run the following command:

.. code-block:: console

    (inspirehep)$ inspirehep alembic revision 'Revision message' -p <parent-revision> --path alembic

Consider that you should use as `parent-revision` the last head revision in order to keep a straightforward hierarchical history
of alembic revisions. In order to find the last revision for `inspirehep` branch run:

.. code-block:: console

    (inspirehep)$ inspirehep alembic heads | grep inspirehep

and the output will be something similar to:

.. code-block:: console

    a82a46d12408 (a26f133d42a9, 9848d0149abd) -> fddb3cfe7a9c (inspirehep) (head), Create inspirehep tables.

From the output we can see that `fddb3cfe7a9c` is the head revision, `a82a46d12408` is it's parent revision and
depends on `(a26f133d42a9, 9848d0149abd)` revisions. For more explanatory output you can run:

.. code-block:: console

    (inspirehep)$ inspirehep alembic heads -vv

and search for `inspirehep` branch.

Upgrade to specific alembic revision
====================================

If you want to execute a specific alembic revision you should run the following command:

.. code-block:: console

    (inspirehep)$ inspirehep alembic upgrade <revision_id>

In a similar way if you want to revert a specific alembic revision run the following command:

.. code-block:: console

    (inspirehep)$ inspirehep alembic downgrade <revision_id>

Alembic stamp
=============

Alembic stores information about every latest revision that has been applied in to an internal database table called `alembic_version_table`.
When we run an upgrade to a specific revision, alembic will search this table and will apply all the revisions sequentially from the last applied
until our own. When we run the following command:

.. code-block:: console

    (inspirehep)$ inspirehep alembic stamp

we tell alembic to update this table with all latest revisions that should have been applied without actually applying them. This command
is useful when we want to make our migrations up-to-date without calling the migration scripts. For example, if we populate a alembic recipe
for creating some new tables but these tables are already present we want to tell alembic to update the version table without applying the
missing revisions because in that case will fail during the trial of recreating the already existing tables.