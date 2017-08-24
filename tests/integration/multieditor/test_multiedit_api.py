from __future__ import absolute_import, division, print_function
import pytest, os, json
from invenio_db import db
from invenio_search import current_search_client as es
from inspirehep.modules.records.api import InspireRecord


@pytest.fixture
def populate_db(app):
    db_records = []
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'assets/test_records.json')) as data_file:
        records = json.load(data_file)
    for record in records:
        db_records.append(InspireRecord.create(record))
    db.session.commit()
    es.indices.refresh('records-hep')
    yield populate_db
    for db_record in db_records:
        db_record._delete(force=True)


def test_multieditor_api(populate_db, api_client):
    # from remote_pdb import RemotePdb
    # RemotePdb('0.0.0.0', 4444).set_trace()
    # with app.test_client() as client:
    response = api_client.get('/multieditor/search/1/foo')
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'assets/test_records.json')) as data_file:
        records = json.load(data_file)
    assert records == json.loads(response.data)['json_records']


