"""
REMOVE ALL REFERENCES IN A WORKFLOW.

This snippet can be used to remove all references in a workflow.

NOTE: use it only if you know what you are doing. References should not be
removed.
"""

from invenio_workflows import workflow_object_class
from invenio_db import db


def remove_references(workflow_id):
    wf = workflow_object_class.get(workflow_id)
    print 'Workflow {} is currently in position {}'.format(workflow_id,
                                                           wf.callback_pos)
    # Note that an empty list is not schema compliant.
    del wf.data['references']
    wf.save()
    db.session.commit()

    res = wf.continue_workflow(start_point='restart_task', delayed=True)
    print 'Workflow {} currently in status {}'.format(workflow_id,
                                                      res.status)
