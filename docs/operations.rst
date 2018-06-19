..
    This file is part of INSPIRE.
    Copyright (C) 2015, 2016 CERN.

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


==========
Operations
==========

INSPIRE operations manual.

Elasticsearch tasks
===================

Simple index remapping
----------------------
This procedure does not take into account the current database, it acts only on
elasticsearch, so any missing records on elasticsearch will not be added, and
any modifications made to the db will not be propagated to elasticsearch.

#. Install `es-cli`_:

.. code-block:: shell

    pip install es-cli

#. Run the remap command:

.. code-block:: shell

    es-cli remap -m path/to/the/new/mapping.json 'https://user:pass@my.es.instan.ce/myindex'


Things to have into account:

* There's no nicer way yet to pass the user/pass
* You can pass more than one '-m\--mapping' option if you are using multiple
  mappings for the same index.
* It creates the new indices with the same aliases that the original had.
* It creates a temporary index in the ES instance, so you will need extra
  space to allocate it.


.. note::

    It's recommended to create a dump/backup of the index prior to the
    remapping, just in case.


Dumping an index
----------------
This procedure will create a set of json files in a directory containing
batches of the index data, including the index metadata (mappings and
similar).

.. code-block:: shell

    es-cli dump_index -o backup_dir 'https://user:pass@my.es.instan.ce/myindex'


This will create a directory called 'backup_dir' that contains two types of
json files, a 'myingex-metadat.json' with the index metadata, and one or more
'myindex-N.json' with the batches of data.


Loading the dump of an index
----------------------------
If you already have dumped an index and you want to load it again, you can run
this:

.. code-block:: shell

    es-cli load_index_dump 'https://user:pass@my.es.instan.ce/myindex' backup_dir


Where 'backup_dir' is the path to the directory where the index dump was
created.



Harvesting and Holding Pen
==========================

Handle records in error state
-----------------------------

Via web interface
~~~~~~~~~~~~~~~~~

1. Visit Holding Pen list and filter for records in error state.

2. If any, you need to investigate why the record workflow failed, check
   the detailed page error report.

3. Sometimes the fix is simply to restart the task again if it is due to
   some circumstantial reasons.

   You can do that from the interface by clicking the "current task" button and hit restart.


Via shell
~~~~~~~~~

1. SSH into any worker machine (usually builder to avoid affecting the machines serving users)

2. Enter the shell and retrieve all records in error state:

.. code-block:: shell

    inspirehep shell


.. code-block:: python

    from invenio_workflows import workflow_object_class, ObjectStatus
    errors = workflows_object_class.query(status=ObjectStatus.ERROR)


3. Get a specific object:

.. code-block:: python

    from invenio_workflows import workflow_object_class
    obj = workflow_object_class.get(1234)
    obj.data  #  Check data
    obj.extra_data   # Check extra data
    obj.status  # Check status
    obj.callback_pos  # Position in current workflow


4. See associated workflow definition:

.. code-block:: python

    from invenio_workflows import workflows
    workflows[obj.workflow.name].workflow   # Associated workflow list of tasks


5. Manipulate position in the workflow

.. code-block:: python

    obj.callback_pos = [1, 2, 3]
    obj.save()


6. Restart workflow in various positions:

.. code-block:: python

    obj.restart_current()  # Restart from current task and continue workflow
    obj.restart_next()  # Skip current task and continue workflow
    obj.restart_previous()  # Redo task before current one and continue workflow


Debug harvested workflows
-------------------------

.. note::

    Added in inspire-crawler => 0.4.0

Sometimes you want to track down the origin of one of the harvest workflows, to
do so you can now use the cli tool to get the log of the crawl, and the bare
result that the crawler outputted:

.. code-block:: shell

    $ # To get the crawl logs of the workflow 1234
    $ inspirehep crawler workflow get_job_logs 1234

    $ # To get the crawl result of the workflow 1234
    $ inspirehep crawler workflow get_job_result 1234


You can also list the crawl jobs, and workflows they started with the commands:

.. code-block:: shell

    $ inspirehep crawler workflow list --tail 50

    $ inspirehep crawler job list --tail 50


There are also a few more options/commands, you can explore them passing the
help flag:

.. code-block:: shell

    $ inspirehep crawler workflow --help

    $ inspirehep crawler job --help


Operations in QA
================

Migrate records in QA
---------------------

The labs database contains a full copy of the legacy records in MARCXML format,
called the mirror. Migrating records from legacy involves connecting to the
right machine and setting up the work environment, populating the mirror from
the file and migrating the records from the mirror, and finally updating the
state of the legacy test database.


Setting up the environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. First of all establish a Kerberos authentication (this can be helpful:
   http://linux.web.cern.ch/linux/docs/kerberos-access.shtml )

2. After you have run the ``kinit`` command and have successfully authenticated you should be able to
   connect to the builder machine:

.. code-block:: shell

    localhost$ ssh username@inspire-qa-worker3-build1.cern.ch

3. Get root access:

.. code-block:: shell

    build1$ sudo -s

4. At this point it's a good idea to initialize a screen so you have something to connect to and reestablish your
   session if something happens to your connection while working remotely to a machine.
   You can use ``byobu``, which is a more user-friendly alternative to ``tmux`` or ``screen``:

.. code-block:: shell

    # This will also reconnect to a running session if any
    build1$ byobu

5. To finish the setup, you need to get into the Inspire virtual environment:


.. code-block:: shell

    build1# workon inspire


Perform the record migration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Make sure you have access to the dump of the records on the local machine,
   for example in your local directory or in ``/tmp`` (otherwise transfer it there
   via scp). You can use either a single ``.xml.gz`` file corresponding to
   a single legacy dump, or a whole ``prodsync.tar`` which besides a full
   first dump contains daily incremental dumps of modified records.

3. Now you can migrate the records, which will be done using the ``inspirehep migrate`` command:

.. note::

      You shouldn't drop the database or destroy the es index as
      the existing records will be overwritten with the ones introduced.

.. code-block:: shell

    build1$ inspirehep migrate file --wait filename

.. note::

      Instead of doing a full migration from file, it is possible to only
      populate the mirror or migrate from the mirror. See ``inspirhep migrate
      --help`` for more information.

4. After migrating the records since we are getting the initial incrementation
   value for our database records from the legacy test database, you should set
   the total number of records migrated to the legacy test incrementation
   table, otherwise every further submission will generate an already existing
   recid, thus failing:

.. code-block:: shell

    #connect to the legacy qa web node
    build1$ ssh inspirevm16.cern.ch

    #connect to the legacy qa db
    legacy_node$ /opt/cds-invenio/bin/dbexec -i

    # to check the autoincrement:
    mysql> SHOW CREATE TABLE bibrec;

    #to set the new value:
    mysql> ALTER TABLE bibrec AUTO_INCREMENT=XXXX;

.. _es-cli: http://es-cli.readthedocs.io
