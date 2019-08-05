"""Remove all entries in the holding pen.

This is a non-reversible, destructive operation performed on the database and
ElasticSearch. USE WITH CAUTION!!!
"""
from invenio_db import db
from invenio_search import current_search

TABLES = ', '.join([
    'crawler_workflows_object',
    'workflows_audit_logging',
    'workflows_buckets',
    'workflows_object',
    'workflows_pending_record',
    'workflows_record_sources',
    'workflows_workflow',
])


db.session.execute('truncate {tables} restart identity'.format(tables=TABLES))
db.session.commit()

list(current_search.delete(index_list=['holdingpen']))
list(current_search.create(ignore_existing=True))
