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

"""Tests for workflows actions."""

from __future__ import absolute_import, division, print_function

import json
import os
import pkg_resources

import pytest

from invenio_db import db
from invenio_search.api import current_search_client as es
from invenio_workflows import workflow_object_class

from inspirehep.modules.workflows.tasks.actions import (
    get_journal_coverage,
    normalize_journal_titles,
)
from inspirehep.modules.workflows.tasks.actions import set_document_type_and_refereed

from utils import _delete_record


@pytest.fixture(scope='function')
def insert_journals_in_db(workflow_app):
    """Temporarily add few journals in the DB"""
    from inspirehep.modules.migrator.tasks import record_insert_or_replace  # imported here because it is a Celery task

    journal_full_1 = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_fully_covered_1.json')))

    journal_partial_1 = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_partially_covered_1.json')))

    journal_partial_2 = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_partially_covered_2.json')))

    journal_no_pro_and_ref = json.loads(pkg_resources.resource_string(
                __name__, os.path.join('fixtures', 'jou_record_refereed.json')))

    journal_pro_and_ref = json.loads(pkg_resources.resource_string(
                __name__, os.path.join('fixtures', 'jou_record_refereed_and_proceedings.json')))

    journal_no_pro_and_not_ref = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_not_refereed_and_no_proceedings.json')))

    journal_pro_and_no_ref_a = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_not_refereed_and_proceedings.json')))

    journal_pro_and_no_ref_b = json.loads(pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'jou_record_not_refereed_and_proceedings_2.json')))

    with db.session.begin_nested():
        record_insert_or_replace(journal_full_1)
        record_insert_or_replace(journal_partial_1)
        record_insert_or_replace(journal_partial_2)
        record_insert_or_replace(journal_no_pro_and_ref)
        record_insert_or_replace(journal_pro_and_ref)
        record_insert_or_replace(journal_no_pro_and_not_ref)
        record_insert_or_replace(journal_pro_and_no_ref_a)
        record_insert_or_replace(journal_pro_and_no_ref_b)
    db.session.commit()
    es.indices.refresh('records-journals')

    yield

    _delete_record('jou', 1936475)
    _delete_record('jou', 1936476)
    _delete_record('jou', 1936477)
    _delete_record('jou', 1936478)
    _delete_record('jou', 1936479)
    _delete_record('jou', 1936480)
    _delete_record('jou', 1936481)
    _delete_record('jou', 1936482)
    es.indices.refresh('records-journals')


def test_normalize_journal_titles_known_journals_with_ref(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "No Proceedings and Refereed J.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936475"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.Ref.J.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936476"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'No.Pro.Ref.J.'
    assert obj.data['publication_info'][2]['journal_title'] == 'Pro.Ref.J.'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_known_journals_with_ref_from_variants(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "No Proceedings and Refereed J. Variant 2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936475"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Proceedings and Refereed J. Variant 3",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936476"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'No.Pro.Ref.J.'
    assert obj.data['publication_info'][2]['journal_title'] == 'Pro.Ref.J.'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_known_journals_no_ref(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "No Proceedings and Refereed J."
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.Ref.J."
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'No.Pro.Ref.J.'
    assert obj.data['publication_info'][2]['journal_title'] == 'Pro.Ref.J.'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_known_journals_wrong_ref(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "No Proceedings and Refereed J.",
                "journal_record": {
                    "$ref": "wrong1"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.Ref.J.",
                "journal_record": {
                    "$ref": "wrong2"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'No.Pro.Ref.J.'
    assert obj.data['publication_info'][2]['journal_title'] == 'Pro.Ref.J.'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936475'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1936476'}


def test_normalize_journal_titles_unknown_journals_with_ref(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Unknown1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/0000000"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Unknown2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1111111"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Unknown1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Unknown2'
    assert obj.data['publication_info'][0]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/0000000'}
    assert obj.data['publication_info'][2]['journal_record'] == {'$ref': 'http://localhost:5000/api/journals/1111111'}


def test_normalize_journal_titles_unknown_journals_no_ref(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Unknown1"
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Unknown2"
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type='hep'
    )

    normalize_journal_titles(obj, None)

    assert obj.data['publication_info'][0]['journal_title'] == 'Unknown1'
    assert obj.data['publication_info'][2]['journal_title'] == 'Unknown2'
    assert 'journal_record' not in obj.data['publication_info'][0]
    assert 'journal_record' not in obj.data['publication_info'][2]


def test_get_journal_coverage_partial(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "article",
            "book",
            "note"
        ],
        "publication_info": [
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Partial.J.1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936481"
                }
            },
            {
                "cnum": "C01-02-03"
            },
            {
                "journal_title": "Partial.J.2",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936482"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    get_journal_coverage(obj, None)

    assert obj.extra_data['journal_coverage'] == 'partial'  # both journals have 'full' coverage


def test_get_journal_coverage_full(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "article",
            "book",
            "note"
        ],
        "publication_info": [
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Full.J.1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936480"
                }
            },
            {
                "cnum": "C01-02-03"
            },
            {
                "journal_title": "Partial.J.1",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936481"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    get_journal_coverage(obj, None)

    assert obj.extra_data['journal_coverage'] == 'full'  # not all journals have 'full' coverage


def test_set_document_type_and_refereed_all_proceedings_none_refereed(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "article",
            "book",
            "note"
        ],
        "publication_info": [
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.No.Ref.J.A.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936478"
                }
            },
            {
                "cnum": "C01-02-03"
            },
            {
                "journal_title": "Pro.No.Ref.J.B.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936479"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' in record['document_type']
    assert not record['refereed']    # both journals have 'referred' False


def test_set_document_type_and_refereed_all_proceedings_none_refereed_not_article(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Pro.No.Ref.J.A.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936478"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.No.Ref.J.B.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936479"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' not in record['document_type']
    assert not record['refereed']  # both journals have 'referred' False


def test_set_document_type_and_refereed_any_refereed_and_proceedings_but_no_conference_paper(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Pro.Ref.J.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936476"
                }
            },
            {
                "cnum": "C01-01-01"
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' not in record['document_type']
    assert record['refereed']


def test_set_document_type_and_refereed_any_refereed_and_proceedings_and_conference_paper(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "conference paper",
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Pro.Ref.J.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936476"
                }
            },
            {
                "cnum": "C01-01-01"
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' in record['document_type']
    assert 'refereed' not in record


def test_set_document_type_and_refereed_any_refereed_and_none_proceedings(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "conference paper",
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "No.Pro.Ref.J.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936475"
                }
            },
            {
                "cnum": "C01-01-01"
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' in record['document_type']
    assert record['refereed']


def test_set_document_type_and_refereed_all_not_refereed(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],
        "titles": [
            "A title"
        ],
        "document_type": [
            "conference paper",
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "No.Pro.No.Ref.J.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936477"
                }
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.No.Ref.J.A.",
                "journal_record": {
                    "$ref": "http://localhost:5000/api/journals/1936478"
                }
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' in record['document_type']
    assert not record['refereed']


def test_set_document_type_and_refereed_no_journal_references(workflow_app, insert_journals_in_db):
    record = {
        "_collections": [
            "Literature"
        ],

        "titles": [
            "A title"
        ],
        "document_type": [
            "article",
            "book",
            "note",
            "report"
        ],
        "publication_info": [
            {
                "journal_title": "Pro.No.Ref.J.A."
            },
            {
                "cnum": "C01-01-01"
            },
            {
                "journal_title": "Pro.No.Ref.J.B."
            }
        ]
    }

    obj = workflow_object_class.create(
        data=record,
        id_user=1,
        data_type="hep"
    )

    set_document_type_and_refereed(obj, None)

    assert 'conference paper' not in record['document_type']
    assert set_document_type_and_refereed(obj, None) is None
