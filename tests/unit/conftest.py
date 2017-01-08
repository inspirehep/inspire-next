# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import os
import shutil
import tempfile

import pytest
from flask_celeryext import FlaskCeleryExt
from six import StringIO

from invenio_mail import InvenioMail
from inspirehep.factory import create_app


@pytest.fixture(scope='session', autouse=True)
def email_app():
    """Email-aware Flask application fixture."""
    app = create_app(
        CFG_SITE_SUPPORT_EMAIL='admin@inspirehep.net',
        INSPIRELABS_FEEDBACK_EMAIL='labsfeedback@inspirehep.net',
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        MAIL_SUPPRESS_SEND=True,
    )
    FlaskCeleryExt(app)

    InvenioMail(app, StringIO())

    with app.app_context():
        yield app


@pytest.fixture(scope='session', autouse=True)
def app():
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()

    os.environ.update(
        APP_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )

    app = create_app(
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
    )

    with app.app_context():
        yield app

    shutil.rmtree(instance_path)


@pytest.fixture
def dummy_response():
    return {
        "_shards": {
            "failed": 0,
            "successful": 10,
            "total": 10
        },
        "hits": {
            "hits": [
                {
                    "_index": "test-index",
                    "_type": "company",
                    "_id": "elasticsearch",
                    "_score": 12.0,

                    "_source": {
                        "city": "Amsterdam",
                        "name": "Elasticsearch",
                    },
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "42",
                    "_score": 11.123,
                    "_parent": "elasticsearch",

                    "_source": {
                        "name": {
                            "first": "Shay",
                            "last": "Bannon"
                        },
                        "lang": "java",
                        "twitter": "kimchy",
                    },
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "47",
                    "_score": 1,
                    "_parent": "elasticsearch",

                    "_source": {
                        "name": {
                            "first": "Honza",
                            "last": "Král"
                        },
                        "lang": "python",
                        "twitter": "honzakral",
                    },
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "53",
                    "_score": 16.0,
                    "_parent": "elasticsearch",
                },
            ],
            "max_score": 12.0,
            "total": 10
        },
        "timed_out": False,
        "took": 123
    }


@pytest.fixture
def dummy_onerecord_response():
    return {
        "_shards": {
            "failed": 0,
            "successful": 10,
            "total": 10
        },
        "hits": {
            "hits": [
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "42",
                    "_score": 11.123,
                    "_parent": "elasticsearch",

                    "_source": {
                        "control_number": 1410174
                    }
                }
            ],
            "max_score": 11.123,
            "total": 1
        },
        "timed_out": False,
        "took": 123
    }


@pytest.fixture
def dummy_tworecord_response():
    return {
        "_shards": {
            "failed": 0,
            "successful": 10,
            "total": 10
        },
        "hits": {
            "hits": [
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "42",
                    "_score": 11.123,
                    "_parent": "elasticsearch",

                    "_source": {
                        "control_number": 1407068,
                        'dois': [
                            {
                                'source': 'Elsevier',
                                'value': u'10.1016/j.ppnp.2015.10.002'
                            }
                        ]
                    }
                },
                {
                    "_index": "test-index",
                    "_type": "employee",
                    "_id": "42",
                    "_score": 11.123,
                    "_parent": "elasticsearch",

                    "_source": {
                        "control_number": 1407079
                    }
                }
            ],
            "max_score": 11.123,
            "total": 2
        },
        "timed_out": False,
        "took": 123
    }


@pytest.fixture
def dummy_empty_response():
    return {
        "_shards": {
            "total": 5,
            "successful": 5,
            "failed": 0
        },
        "hits": {
            "total": 0,
            "max_score": 'null',
            "hits": []
        }
    }
