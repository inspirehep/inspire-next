"""RESOLVE MISSMATCH VERSION BETWEEN LABS AND LEGACY."""

from invenio_workflows import workflow_object_class
from inspirehep.utils.record_getter import get_db_record
from invenio_db import db


def resolve_missmatch_version_with_legacy(workflow_id, legacy_revision):
    """Revert record revision to be the same with the legacy version.

    Example ::
        resolve_missmatch_version_with_legacy(1236029, '20180926071008.0')
    """
    obj = workflow_object_class.get(workflow_id)
    record = get_db_record('lit', obj.data['control_number'])
    revisions = [revision for revision in record.revisions if revision.get('legacy_version') == legacy_revision]

    if not revisions:
        print('revision {} not found'.format(legacy_revision))
        return None

    print('revision found.')
    revision = revisions.pop()
    record.clear()
    record.update(revision, skip_files=True)
    record.commit()
    obj.callback_pos = [0]
    obj.save()
    db.session.commit()
    response = obj.continue_workflow(delayed=True)
    print 'Workflow {} currently in status {}'.format(workflow_id, response.status)
