"""
CHANGE A GIVEN RECORD.

This snippet can be used to find and modify a record through the shell, given
its control number.
"""

from contextlib import contextmanager
from copy import deepcopy

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.records.api import InspireRecord


@contextmanager
def modify_record(pid_type, pid_value):
    """
    Context manager to modify metadata of a single record by PID.

    The context manager makes a `dict` containing all metadata of the record
    available inside the ``with`` block. Modifying that ``dict`` will perform
    the modifications at the end of the block.

    Example:
        >>> with modify_record('lit', 1505221) as data:
        ...     data['titles'][0] = {'title': 'My new title'}
    """
    uuid = PersistentIdentifier.query.filter_by(pid_type=pid_type, pid_value=str(pid_value)).one().object_uuid
    record = InspireRecord.get_record(uuid)
    data = deepcopy(record)

    yield data

    record.clear()
    record.update(data)
    record.commit()
    db.session.commit()
