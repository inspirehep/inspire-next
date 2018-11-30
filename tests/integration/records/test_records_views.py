# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import json

from invenio_db import db
from invenio_search import current_search_client as es

from utils import _delete_record
from inspirehep.modules.records.api import InspireRecord


def test_literature_citations_api_with_results(app, api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()
    db.session.commit()

    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citation_count": 2,
        "citations": [
            {
                "control_number": 222,
                "titles": [
                    {
                        "title": "Frank Castle"
                    }
                ]
            },
            {
                "control_number": 333,
                "titles": [
                    {
                        "title": "Luke Cage"
                    }
                ]
            }
        ]
    }

    expected_metadata['citations'].sort()
    result['metadata']['citations'].sort()

    assert response.status_code == 200
    assert expected_metadata == result['metadata']

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)


def test_literature_citations_api_sorted_by_earliest_date(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'preprint_date': '2013-10-08',
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2015-10-08',
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()

    record_json_ref_3 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'preprint_date': '2015-11-08',
        'control_number': 444,
        'titles': [
            {
                'title': 'John Doe',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_3 = InspireRecord.create(record_json_ref_3)
    record_ref_3.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citation_count": 3,
        "citations": [
            {
                "control_number": 444,
                "titles": [
                    {
                        "title": "John Doe"
                    }
                ],
                "earliest_date": "2015-11-08"
            },
            {
                "control_number": 333,
                "titles": [
                    {
                        "title": "Luke Cage"
                    }
                ],
                "earliest_date": "2015-10-08"
            },
            {
                "control_number": 222,
                "titles": [
                    {
                        "title": "Frank Castle"
                    }
                ],
                "earliest_date": "2013-10-08"
            }
        ]
    }

    assert response.status_code == 200
    assert expected_metadata == result['metadata']

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)
    _delete_record('lit', 444)


def test_literature_citations_api_without_results(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citation_count": 0,
        "citations": [],
    }

    assert response.status_code == 200
    assert expected_metadata == result['metadata']

    _delete_record('lit', 111)


def test_literature_citations_api_with_parameter_page_1(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations?size=1&page=1',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = [
        {
            "citation_count": 2,
            "citations": [
                {
                    "control_number": 222,
                    "titles": [
                        {
                            "title": "Frank Castle"
                        }
                    ]
                },
            ]
        },
        {
            "citation_count": 2,
            "citations": [
                {
                    "control_number": 333,
                    "titles": [
                        {
                            "title": "Luke Cage"
                        }
                    ]
                },
            ]
        }
    ]

    assert response.status_code == 200
    assert result['metadata'] in expected_metadata

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)


def test_literature_citations_api_with_parameter_page_2(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations?size=1&page=2',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = [
        {
            "citation_count": 2,
            "citations": [
                {
                    "control_number": 222,
                    "titles": [
                        {
                            "title": "Frank Castle"
                        }
                    ]
                },
            ]
        },
        {
            "citation_count": 2,
            "citations": [
                {
                    "control_number": 333,
                    "titles": [
                        {
                            "title": "Luke Cage"
                        }
                    ]
                },
            ]
        }
    ]

    assert response.status_code == 200
    assert result['metadata'] in expected_metadata

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)


def test_literature_citations_api_with_malformed_parameters(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations?page=-20',
        headers={'Accept': 'application/json'}
    )

    assert response.status_code == 400

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)


def test_literature_citations_api_with_not_existing_pid_value(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/444/citations',
        headers={'Accept': 'application/json'}
    )

    assert response.status_code == 404

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)


def test_literature_citations_api_with_full_citing_record(api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature']
    }
    record = InspireRecord.create(record_json)
    record.commit()

    record_json_ref_1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 222,
        'titles': [
            {
                'title': 'Frank Castle',
            },
        ],
        'authors': [
            {
                "full_name": "Urhan, Ahmet",
            }
        ],
        'publication_info': [
            {
                "artid": "HAL Id : hal-01735421, https://hal.archives-ouvertes.fr/hal-01735421",
                "page_start": "1",
            }
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_1 = InspireRecord.create(record_json_ref_1)
    record_ref_1.commit()

    record_json_ref_2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 333,
        'titles': [
            {
                'title': 'Luke Cage',
            },
        ],
        'references': [
            {
                'record': {
                    '$ref': record._get_ref()
                }
            }
        ],
        '_collections': ['Literature']
    }
    record_ref_2 = InspireRecord.create(record_json_ref_2)
    record_ref_2.commit()

    db.session.commit()
    es.indices.refresh('records-hep')

    response = api_client.get(
        '/literature/111/citations',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    result['metadata']['citations'].sort()

    expected_metadata = {
        "citation_count": 2,
        "citations": [
            {
                'authors': [
                    {
                        "full_name": "Urhan, Ahmet",
                        "first_name": "Ahmet",
                        "last_name": "Urhan",
                        "signature_block": "URANa",
                        "uuid": result['metadata']['citations'][1]['authors'][0]['uuid']
                    }
                ],
                'control_number': 222,
                'titles': [
                    {
                        'title': 'Frank Castle',
                    },
                ]
            },
            {
                "control_number": 333,
                "titles": [
                    {
                        "title": "Luke Cage"
                    }
                ]
            }
        ]
    }

    assert response.status_code == 200

    expected_metadata['citations'].sort()

    assert expected_metadata == result['metadata']

    _delete_record('lit', 111)
    _delete_record('lit', 222)
    _delete_record('lit', 333)
