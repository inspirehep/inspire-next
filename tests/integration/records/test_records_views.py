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

from factories.db.invenio_records import TestRecordMetadata


def test_literature_citations_api_with_results(isolated_api_client):
    record_json = {
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    record_json_ref_1 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_1)

    record_json_ref_2 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_2)

    response = isolated_api_client.get(
        '/literature/111/citations',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citations": [
            {
                "_collections": [
                    "Literature"
                ],
                "control_number": 222,
                "document_type": [
                    "article"
                ],
                "number_of_references": 1,
                "titles": [
                    {
                        "title": "Frank Castle"
                    }
                ]
            },
            {
                "_collections": [
                    "Literature"
                ],
                "control_number": 333,
                "document_type": [
                    "article"
                ],
                "number_of_references": 1,
                "titles": [
                    {
                        "title": "Luke Cage"
                    }
                ]
            }
        ]
    }

    assert response.status_code == 200
    assert expected_metadata == result['metadata']


def test_literature_citations_api_without_results(isolated_api_client):
    record_json = {
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    response = isolated_api_client.get(
        '/literature/111/citations',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citations": [],
    }

    assert response.status_code == 200
    assert expected_metadata == result['metadata']


def test_literature_citations_api_with_parameter_page_1(isolated_api_client):
    record_json = {
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    record_json_ref_1 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_1)

    record_json_ref_2 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_2)

    response = isolated_api_client.get(
        '/literature/111/citations?size=1&page=1',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citations": [
            {
                "_collections": [
                    "Literature"
                ],
                "control_number": 222,
                "document_type": [
                    "article"
                ],
                "number_of_references": 1,
                "titles": [
                    {
                        "title": "Frank Castle"
                    }
                ]
            },
        ]
    }

    assert response.status_code == 200
    assert expected_metadata == result['metadata']


def test_literature_citations_api_with_parameter_page_2(isolated_api_client):
    record_json = {
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    record_json_ref_1 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_1)

    record_json_ref_2 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_2)

    response = isolated_api_client.get(
        '/literature/111/citations?size=1&page=2',
        headers={'Accept': 'application/json'}
    )
    result = json.loads(response.get_data(as_text=True))

    expected_metadata = {
        "citations": [
            {
                "_collections": [
                    "Literature"
                ],
                "control_number": 333,
                "document_type": [
                    "article"
                ],
                "number_of_references": 1,
                "titles": [
                    {
                        "title": "Luke Cage"
                    }
                ]
            }
        ]
    }

    assert response.status_code == 200
    assert expected_metadata == result['metadata']


def test_literature_citations_api_with_malformed_parameters(isolated_api_client):
    record_json = {
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    record_json_ref_1 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_1)

    record_json_ref_2 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_2)

    response = isolated_api_client.get(
        '/literature/111/citations?page=-20',
        headers={'Accept': 'application/json'}
    )

    assert response.status_code == 400


def test_literature_citations_api_with_not_existing_pid_value(isolated_api_client):
    record_json = {
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
    }
    record = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    record_json_ref_1 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_1)

    record_json_ref_2 = {
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
        ]
    }
    TestRecordMetadata.create_from_kwargs(json=record_json_ref_2)

    response = isolated_api_client.get(
        '/literature/444/citations',
        headers={'Accept': 'application/json'}
    )

    assert response.status_code == 404
