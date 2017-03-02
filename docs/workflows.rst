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



Ingestion of records (Workflows)
********************************


Inspire-next retrieves new records every day from several sources, such as:
    * External sites (arXiv, Proceedings of Science, ...).
    * Users, through submission forms.

The records harvested from external sites are all pulled in by `hepcrawl`_,
that is periodically executed by a `celery beat`_ task.

The Users also suggest new records, both literature records and author records
by using the submission forms.

One of the main goals of Inspire is the high quality of the information it
provides, so in order to achieve that, every record is carefully and rigorously
revised by our team of curators befor finally getting accepted inside the
Inspire database.

Below there's a small diagram summarizing the process.

.. image:: images/workflows_overview.png
    :height: 660
    :width: 660




Handle workflows in error state
*******************************

Via web interface
-----------------

1. Visit Holding Pen list and filter for records in error state.

2. If any, you need to investigate why the record workflow failed, check
   the detailed page error report.

3. Sometimes the fix is simply to restart the task again if it is due to
   some circumstantial reasons.

   You can do that from the interface by clicking the "current task" button
   and hit restart.


Via shell
---------

1. SSH into any worker machine (usually builder to avoid affecting the
   machines serving users)

2. Enter the shell and retrieve all records in error state:

.. code-block:: shell

    inspirehep shell


.. code-block:: python

    from invenio_workflows import workflow_object_class, ObjectStatus
    errors = workflow_object_class.query(status=ObjectStatus.ERROR)

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
    # to persist the change in the db
    from invenio_db import db
    db.session.commit()


6. Restart workflow in various positions:

.. code-block:: python

    obj.restart_current()  # Restart from current task and continue workflow
    obj.restart_next()  # Skip current task and continue workflow
    obj.restart_previous()  # Redo task before current one and continue workflow

    # If the workflow is in inital state, you can start it from scratch
    from invenio_workflows import start
    start('article', object_id=obj.id)
    # or for an author workflow
    start('author', object_id=obj.id)

.. _hepcrawl: https://github.com/inspirehep/hepcrawl
.. _celery beat: http://docs.celeryproject.org/en/latest/reference/celery.beat.html
