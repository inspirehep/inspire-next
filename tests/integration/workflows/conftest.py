# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function
import imp
from pdb import Pdb

import random
import uuid

import mock
import os

import pkg_resources
from sqlalchemy import MetaData, create_engine
from inspirehep.utils.utils import include_table_check
import pytest
import re
import requests_mock
import sys

from flask_alembic import Alembic
from invenio_db import db
from invenio_db.utils import drop_alembic_version_table
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search
from sqlalchemy.ext.declarative import declarative_base

from inspirehep.factory import create_app as inspire_create_app
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions, init_authentication_token
from inspirehep.modules.records.api import InspireRecord
from helpers.cleanups import es_cleanup, db_cleanup
# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))


from factories.db.invenio_records import (
    cleanup as invenio_records_factory_cleanup,
)  # noqa


from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


HIGGS_ONTOLOGY = '''<?xml version="1.0" encoding="UTF-8" ?>

<rdf:RDF xmlns="http://www.w3.org/2004/02/skos/core#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

    <Concept rdf:about="http://cern.ch/thesauri/HEPontology.rdf#Higgsparticle">
        <prefLabel xml:lang="en">Higgs particle</prefLabel>
        <altLabel xml:lang="en">Higgs boson</altLabel>
        <hiddenLabel xml:lang="en">Higgses</hiddenLabel>
        <note xml:lang="en">core</note>
    </Concept>

</rdf:RDF>
'''


@pytest.fixture(scope='module')
def higgs_ontology(tmpdir_factory):
    ontology = tmpdir_factory.mktemp('data').join('HEPont.rdf')
    ontology.write(HIGGS_ONTOLOGY)
    yield str(ontology)


@pytest.fixture(scope="module")
def app_config(instance_path, app_config, higgs_ontology):
    # add extra global config if you would like to customize the config
    # for a specific test you can change create fixture per-directory
    # using ``conftest.py`` or per-file.
    RT_URL = "http://rt.inspire"
    GROBID_URL = "http://grobid_url.local"
    app_config["FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT"]=True
    app_config['CELERY_TASK_ALWAYS_EAGER']=True
    app_config['CELERY_CACHE_BACKEND']='memory'
    app_config['CELERY_TASK_EAGER_PROPAGATES']=True
    app_config['CELERY_RESULT_BACKEND']='cache'
    app_config['CFG_BIBCATALOG_SYSTEM_RT_URL']=RT_URL
    app_config['CLASSIFIER_API_URL']="http://example.com/classifier"
    app_config['DEBUG']=False
    app_config['GROBID_URL']=GROBID_URL
    app_config['HEP_ONTOLOGY_FILE']=higgs_ontology
    app_config['PRODUCTION_MODE']=True
    app_config['LEGACY_ROBOTUPLOAD_URL']=(
        'http://localhost:1234'
    )
    app_config['MAGPIE_API_URL']="http://example.com/magpie"
    app_config['WORKFLOWS_FILE_LOCATION']="/"
    app_config['WORKFLOWS_MATCH_REMOTE_SERVER_URL']="http://legacy_search.endpoint/"
    app_config['WTF_CSRF_ENABLED']=False
    app_config['ALEMBIC_SKIP_TABLES'] = ["workflows_record_sources", "accounts_user", "accounts_role"]
    app_config['ALEMBIC_CONTEXT'] = {
    "version_table": "inspirehep_alembic_version",
    "include_object": include_table_check,
}
    app_config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql+psycopg2://inspirehep:inspirehep@localhost/test-inspirehep"
    return app_config



@pytest.fixture(scope="module")
def create_app():
    return inspire_create_app


@pytest.fixture(scope='module')
def base_app(create_app, app_config, request, default_handler):
    RT_URL = "http://rt.inspire"
    with requests_mock.Mocker() as m:
        m.register_uri(
            requests_mock.ANY,
            re.compile("http://web:8000/literature/.*"),
            status_code=200,
        )      
        m.register_uri(
            requests_mock.ANY,
            re.compile('.*' + RT_URL + '.*'),
            status_code=200,
            text='Status 200'
        )
        create_app = getattr(request.module, 'create_app', create_app)
        app_ = create_app(**app_config)
        app_.extensions['invenio-search']
        # See documentation for default_handler
        if default_handler:
            app_.logger.addHandler(default_handler)
        yield app_


@pytest.fixture(scope="function")
def workflow_app(base_app, db, es_clear):
    with base_app.app_context():
        with mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.apply_async'):
            yield base_app


@pytest.fixture
def workflow_api(workflow_app):
    """Flask API application."""
    yield workflow_app.wsgi_app.mounts['/api']


@pytest.fixture
def workflow_api_client(workflow_api):
    """Flask test client for the API application."""
    with workflow_api.test_client() as client:
        yield client


# @pytest.fixture(scope="function")
# def create_all(app):
    # with db.engine.connect() as conn:
    #     metadata = MetaData(db.engine, reflect=True)
    #     tables_to_create = db.metadata.tables.copy()
    #     if 'workflows_record_sources' in tables_to_create:
    #         del tables_to_create['workflows_record_sources']
    #     metadata.create_all(tables=tables_to_create.values())
    # alembic = Alembic(app=app)
    # alembic.upgrade()
    # db.metadata.create_all()

    # _es = app.extensions['invenio-search']
    # list(_es.create(ignore=[400]))

    # init_all_storage_paths()
    # init_users_and_permissions()
    # init_authentication_token()



@pytest.fixture(autouse=True)
def cleanup_workflows(workflow_app):
    # db.session.close_all()
    # drop_all(app=workflow_app)
    # create_all(app=workflow_app)
    invenio_records_factory_cleanup()



@pytest.fixture(scope="module")
def database(appctx):
    """Setup database."""
    from invenio_db import db as db_

    db_cleanup(db_)
    yield db_
    db_.session.remove()


@pytest.fixture(scope="function")
def db_(database):
    """Creates a new database session for a test.
    Scope: function
    You must use this fixture if your test connects to the database. The
    fixture will set a save point and rollback all changes performed during
    the test (this is much faster than recreating the entire database).
    """
    import sqlalchemy as sa

    connection = database.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = database.create_scoped_session(options=options)

    session.begin_nested()

    # FIXME: attach session to all factories
    # https://github.com/pytest-dev/pytest-factoryboy/issues/11#issuecomment-130521820
    # BaseFactory._meta.sqlalchemy_session = session
    # RecordMetadataFactory._meta.sqlalchemy_session = session
    # PersistentIdentifierFactory._meta.sqlalchemy_session = session
    # LegacyRecordsMirrorFactory._meta.sqlalchemy_session = session
    # `session` is actually a scoped_session. For the `after_transaction_end`
    # event, we need a session instance to listen for, hence the `session()`
    # call.

    @sa.event.listens_for(session(), "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.expire_all()
            session.begin_nested()

    old_session = database.session
    database.session = session

    yield database
    session.remove()
    transaction.rollback()
    connection.close()
    database.session = old_session


@pytest.fixture(scope="function")
def db(db_):
    yield db_


@pytest.fixture
def mocked_external_services(workflow_app):
    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_1407.7587.xml'
        )
    )
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile('.*(indexer|localhost).*'),
            real_http=True,
        )
        requests_mocker.register_uri(
            'POST',
            re.compile(
                'https?://localhost:1234.*',
            ),
            text=u'[INFO]',
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['WORKFLOWS_MATCH_REMOTE_SERVER_URL'] +
                '.*'
            ),
            status_code=200,
            json=[],
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['CFG_BIBCATALOG_SYSTEM_RT_URL'] +
                '/ticket/new.*'
            ),
            status_code=200,
            text='RT/3.8.7 200 Ok\n\n# Ticket 1 created.\n# Ticket 1 updated.'
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['CFG_BIBCATALOG_SYSTEM_RT_URL'] +
                '/ticket/.*/comment'
            ),
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['CFG_BIBCATALOG_SYSTEM_RT_URL'] +
                '/ticket/.*/edit'
            ),
            status_code=200,
            text='Irrelevant part 1 of message \nIrrelevant part 2 of message \n# Ticket 1 updated.'
        )
        requests_mocker.register_uri(
            'POST', 'http://grobid_url.local/api/processHeaderDocument',
            text=grobid_response.decode('utf-8'),
            headers={'content-type': 'application/xml'},
            status_code=200,
        )
        requests_mocker.register_uri(
            'POST', 'http://grobid_url.local/api/processFulltextDocument',
            headers={'content-type': 'application/xml'},
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            "{inspirehep_url}/api/literature/workflows_sources".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            ),
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile("{inspirehep_url}/api/literature.*".format(
            inspirehep_url=workflow_app.config["INSPIREHEP_URL"]
            )),
            status_code=200,
        )      
        if 'INSPIREHEP_URL' in workflow_app.config:
            # HEP record upload
            requests_mocker.register_uri(
                'POST',
                re.compile('.*' + workflow_app.config['INSPIREHEP_URL'] + '/(literature|aurhors)/?'),
                status_code=201,
                json={
                    "metadata": {
                        "control_number": random.randint(10000, 99999),
                    },
                    "uuid": str(uuid.uuid4())
                }
            )

        yield requests_mocker


@pytest.fixture
def record_from_db(workflow_app):
    from invenio_db import db

    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'Fancy title for a new record'}],
        'arxiv_eprints': [
            {'categories': ['hep-th'], 'value': '1407.7587'}
        ],
        'control_number': 1234,
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}]
    }
    record = InspireRecord.create(json, id_=None, skip_files=True)
    record.commit()
    rec_uuid = record.id

    db.session.commit()
    current_search.flush_and_refresh('records-hep')

    yield record

    record = InspireRecord.get_record(rec_uuid)
    pid = PersistentIdentifier.get(
        pid_type='lit',
        pid_value=record['control_number']
    )

    pid.unassign()
    pid.delete()
    record.delete()
    record.commit()


@pytest.fixture
def record_to_merge(workflow_app):
    from invenio_db import db

    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': [
            'Literature'
        ],
        'authors': [
            {
                'full_name': 'Jessica, Jones',
            },
        ],
        'document_type': [
            'thesis'
        ],
        'number_of_pages': 100,
        'preprint_date': '2016-11-16',
        'public_notes': [
            {
                'source': 'arXiv',
                'value': '100 pages, 36 figures'
            }
        ],
        'titles': [
            {
                'title': 'Alias Investigations'
            }
        ],
        'dois': [
            {
                'value': '10.1007/978-3-319-15001-7'
            }
        ],
    }
    record = InspireRecord.create(json, id_=None, skip_files=True)
    record.commit()
    rec_uuid = record.id

    db.session.commit()
    current_search.flush_and_refresh('records-hep')

    yield record

    record = InspireRecord.get_record(rec_uuid)
    pid = PersistentIdentifier.get(
        pid_type='lit',
        pid_value=record['control_number']
    )

    pid.unassign()
    pid.delete()
    record.delete()
    record.commit()


@pytest.fixture(scope='module')
def es(appctx):
    from invenio_search import current_search, current_search_client
    from helpers.cleanups import _es_create_indexes
    from pytest_invenio.fixtures import _es_delete_indexes
    appctx.extensions['invenio-search'].register_mappings('records', 'inspirehep.modules.records.mappings')
    _es_create_indexes(current_search)
    yield current_search_client
    _es_delete_indexes(current_search)


@pytest.fixture(scope="function")
def es_clear(es):
    es_cleanup(es)
    yield es
