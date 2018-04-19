"""
REMOVE ALL RECORDS WITHOUT CONTROL NUMBER.

This snippet can be used to find and completely remove all records without
a control number. It first finds the records and then deletes the related
objects in the following models:
Bucket, RecordsBuckets, ObjectVersion, PersistentIdentifier, RecordMetadata.
"""

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import not_, type_coerce

from invenio_db import db
from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.models import RecordsBuckets
from invenio_records.models import RecordMetadata


def _delete_record(record):
    rec_bucket = RecordsBuckets.query.filter(RecordsBuckets.record == record).one()
    bucket = rec_bucket.bucket
    ObjectVersion.query.filter(ObjectVersion.bucket == bucket).delete()
    db.session.delete(bucket)
    db.session.delete(rec_bucket)
    PersistentIdentifier.query.filter(PersistentIdentifier.object_uuid == record.id).delete()
    db.session.delete(record)
    db.session.commit()


def delete_records_without_control_number():
    """
    Find all record without a control number and delete them.
    """
    # Find all records without control_number.
    records = RecordMetadata.query.filter(not_(
        type_coerce(RecordMetadata.json, JSONB).has_key(
            'control_number'))).all()

    for record in records:
        _delete_record(record)


def delete_record_by_pid(pid_type, pid_value):
    """
    Delete a single record by PID.

    Example:
        >>> delete_record_by_pid('lit', 1667913)
    """
    record = RecordMetadata.query.filter(RecordMetadata.id == PersistentIdentifier.object_uuid)\
        .filter(PersistentIdentifier.pid_value == str(pid_value),
                PersistentIdentifier.pid_type == pid_type).one()

    _delete_record(record)
