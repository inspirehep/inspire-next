"""
REMOVE ALL RECORDS WITHOUT CONTROL NUMBER.

This snippet can be used to restart workflows.
"""

from invenio_workflows import workflow_object_class
from invenio_db import db


def restart_workflow(workflow_id, position=[0]):
    wf = workflow_object_class.get(workflow_id)
    print 'Workflow {} is currently in position {}'.format(workflow_id,
                                                           wf.callback_pos)
    wf.callback_pos = position
    wf.save()

    db.session.commit()

    res = wf.continue_workflow(delayed=True)
    print 'Workflow {} currently in status {}'.format(workflow_id,
                                                      res.status)
