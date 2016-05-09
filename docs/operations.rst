==========
Operations
==========

INSPIRE operations manual.

**IN DEVELOPMENT**

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

    # TODO Invenio 3 code


3. Get a specific object:

.. code-block:: python

    from invenio_workflows import WorkflowObject
    obj = WorkflowObject.query.get(1234)
    obj.data  #  Check data
    obj.extra_data   # Check extra data
    obj.status  # Check status
    obj.get_error_message()  # Get error traceback (if any)
    obj.callback_pos  # Position in current workflow

    from invenio_workflows import workflows
    workflows[obj.workflow.name].workflow   # Associated workflow list of tasks

    obj.continue_workflow("restart_task")  # Restart from current task and continue workflow
    obj.continue_workflow()  # Skip current task and continue workflow
    obj.continue_workflow("previous_task")  # Redo task before current one and continue workflow
