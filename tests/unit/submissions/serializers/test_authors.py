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

from inspire_schemas.api import load_schema, validate

from inspirehep.modules.submissions.serializers.schemas import Author


def test_dump_author_advisors():
    data = {
        'advisors': [
            {
                'degree_type': 'bachelor',
                'ids': [
                    {'schema': 'DESY', 'value': 'DESY-55924820881'},
                    {'schema': 'SCOPUS', 'value': '7039712595'},
                    {'schema': 'SCOPUS', 'value': '8752067273'}
                ],
                'name': 'occaecat qui sint in id',
                'record': {'$ref': 'http://1js40iZ'}
            },
        ]
    }
    schema = load_schema('authors')
    subschema = schema['properties']['advisors']

    result = Author().dump(data).data
    expected = {
        'advisors': [
            {
                'degree_type': 'bachelor',
                'ids': [
                    {'schema': 'DESY', 'value': 'DESY-55924820881'},
                    {'schema': 'SCOPUS', 'value': '7039712595'},
                    {'schema': 'SCOPUS', 'value': '8752067273'}
                ],
                'name': 'occaecat qui sint in id',
                'record': {'$ref': 'http://1js40iZ'}
            },
        ]
    }

    assert validate(data['advisors'], subschema) is None
    assert expected == result


def test_load_author_advisors():
    data = {
        'advisors': [
            {
                'degree_type': 'bachelor',
                'ids': [
                    {'schema': 'DESY', 'value': 'DESY-55924820881'},
                    {'schema': 'SCOPUS', 'value': '7039712595'},
                    {'schema': 'SCOPUS', 'value': '8752067273'},
                ],
                'name': 'occaecat qui sint in id',
                'record': {'$ref': 'http://1js40iZ'}
            },
        ]
    }
    schema = load_schema('authors')
    subschema = schema['properties']['advisors']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'advisors': [
            {
                'curated_relation': False,
                'degree_type': 'bachelor',
                'name': 'Id, Occaecat Qui Sint In',
                'ids': [
                    {'schema': 'DESY', 'value': 'DESY-55924820881'},
                    {'schema': 'SCOPUS', 'value': '7039712595'},
                    {'schema': 'SCOPUS', 'value': '8752067273'}
                ],
                'record': {'$ref': 'http://1js40iZ'}
            },
        ]
    }

    assert validate(result['advisors'], subschema) is None
    assert expected == result


def test_dump_author_acquisition_source():
    data = {
        'acquisition_source': {
            'method': 'submitter',
            'submission_number': '12',
            'internal_uid': 1,
            'email': 'albert.einstein@hep.ed',
            'orcid': '0000-0001-8528-2091',
        },
    }
    schema = load_schema('authors')
    subschema = schema['properties']['acquisition_source']

    result = Author().dump(data).data
    expected = {
        'acquisition_source': {
            'method': 'submitter',
            'submission_number': '12',
            'internal_uid': 1,
            'email': 'albert.einstein@hep.ed',
            'orcid': '0000-0001-8528-2091',
        },
    }

    assert validate(data['acquisition_source'], subschema) is None
    assert expected == result


def test_load_author_acquisition_source():
    data = {
        'acquisition_source': {
            'method': 'submitter',
            'submission_number': '12',
            'internal_uid': 1,
            'email': 'albert.einstein@hep.ed',
            'orcid': '0000-0001-8528-2091',
        },
    }
    schema = load_schema('authors')
    subschema = schema['properties']['acquisition_source']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'acquisition_source': {
            'method': 'submitter',
            'submission_number': '12',
            'internal_uid': 1,
            'email': 'albert.einstein@hep.ed',
            'orcid': '0000-0001-8528-2091',
        },
    }

    assert validate(result['acquisition_source'], subschema) is None
    assert expected == result


def test_dump_author_arxiv_categories():
    data = {
        'arxiv_categories': [
            'math.CV',
            'astro-ph.HE',
            'econ.EM',
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['arxiv_categories']

    result = Author().dump(data).data
    expected = {
        'arxiv_categories': [
            'math.CV',
            'astro-ph.HE',
            'econ.EM',
        ],
    }

    assert validate(data['arxiv_categories'], subschema) is None
    assert expected == result


def test_load_author_arxiv_categories():
    data = {
        'arxiv_categories': [
            'math.CV',
            'astro-ph.HE',
            'econ.EM',
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['arxiv_categories']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'arxiv_categories': [
            'math.CV',
            'astro-ph.HE',
            'econ.EM',
        ],
    }

    assert validate(result['arxiv_categories'], subschema) is None
    assert expected == result


def test_dump_author_blog():
    data = {
        'urls': [
            {
                'value': 'https:/myblog.com',
                'description': 'blog',
            },
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['urls']

    result = Author().dump(data).data
    expected = {
        'blog': 'https:/myblog.com',
        'websites': [
            'https:/myblog.com',
        ],
    }

    assert validate(data['urls'], subschema) is None
    assert expected == result


def test_dump_author_without_blog():
    data = {
        'urls': [
            {
                'value': 'https://www.linkedin.com/in/example-12345/',
                'description': 'something_else',
            },
        ],
    }

    result = Author().dump(data).data
    expected = {
        'websites': [
            'https://www.linkedin.com/in/example-12345/',
        ]
    }

    assert expected == result


def test_load_author_blog():
    data = {
        'blog': 'https:/myblog.com',
    }
    schema = load_schema('authors')
    subschema = schema['properties']['urls']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'urls': [
            {
                'value': 'https:/myblog.com',
                'description': 'blog',
            },
        ],
    }
    assert validate(expected['urls'], subschema) is None
    assert expected == result


def test_dump_author_linkedin():
    data = {
        'ids': [
            {
                'value': 'https:/linkedin.com',
                'schema': 'LINKEDIN',
            },
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    result = Author().dump(data).data
    expected = {
        'linkedin': 'https:/linkedin.com',
    }

    assert validate(data['ids'], subschema) is None
    assert expected == result


def test_load_author_linkedin():
    data = {
        'linkedin': 'https:/linkedin.com',
    }
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'ids': [
            {
                'schema': 'LINKEDIN',
                'value': 'https:/linkedin.com',
            },
        ],
    }

    assert validate(expected['ids'], subschema) is None
    assert expected == result


def test_dump_author_twitter():
    data = {
        'ids': [
            {
                'value': 'https:/twitter.com',
                'schema': 'TWITTER',
            },
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    result = Author().dump(data).data
    expected = {
        'twitter': 'https:/twitter.com',
    }

    assert validate(data['ids'], subschema) is None
    assert expected == result


def test_load_author_twitter():
    data = {
        'twitter': 'https:/twitter.com',
    }
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'ids': [
            {
                'schema': 'TWITTER',
                'value': 'https:/twitter.com',
            },
        ],
    }

    assert validate(expected['ids'], subschema) is None
    assert expected == result


def test_dump_author_orcid():
    data = {
        'ids': [
            {
                'value': '0000-0002-7638-5686',
                'schema': 'ORCID',
            },
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    result = Author().dump(data).data
    expected = {
        'orcid': '0000-0002-7638-5686'
    }

    assert validate(data['ids'], subschema) is None
    assert expected == result


def test_load_author_orcid():
    data = {
        'orcid': '0000-0002-7638-5686'
    }
    schema = load_schema('authors')
    subschema = schema['properties']['ids']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'ids': [
            {
                'value': '0000-0002-7638-5686',
                'schema': 'ORCID',
            },
        ],
    }

    assert validate(expected['ids'], subschema) is None
    assert expected == result


def test_dump_author_comments():
    data = {
        '_private_notes': [
            {
                'value': 'THIS IS A NOTE',
            },
        ],
    }
    schema = load_schema('authors')
    subschema = schema['properties']['_private_notes']

    result = Author().dump(data).data

    assert validate(data['_private_notes'], subschema) is None
    assert 'comments' not in result


def test_load_author_comments():
    data = {
        'comments': 'THIS IS A NOTE',
    }
    schema = load_schema('authors')
    subschema = schema['properties']['_private_notes']

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        '_private_notes': [
            {
                'value': 'THIS IS A NOTE',
            },
        ],
    }

    assert validate(expected['_private_notes'], subschema) is None
    assert expected == result


def test_dump_author_display_name():
    data = {
        'name': {
            'preferred_name': 'Jessica Jones',
        }
    }

    result = Author().dump(data).data
    expected = {
        'display_name': 'Jessica Jones',
    }

    assert expected == result


def test_load_author_display_name():
    data = {
        'display_name': 'Jessica Jones'
    }

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'name': {
            'preferred_name': 'Jessica Jones'
        }
    }

    assert expected == result


def test_dump_author_native_name():
    data = {
        'name': {
            'value': 'Jones, Jessica',
            'native_names': [
                'Τζέσικα Τζόουνς',
            ]
        }
    }

    result = Author().dump(data).data
    expected = {
        'native_name': 'Τζέσικα Τζόουνς',
        'family_name': 'Jones',
        'given_name': 'Jessica',
    }

    assert expected == result


def test_load_author_native_name():
    data = {
        'native_name': 'Τζέσικα Τζόουνς',
        'family_name': 'Jones',
        'given_name': 'Jessica',
    }

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'name': {
            'value': 'Jones, Jessica',
            'native_names': [
                'Τζέσικα Τζόουνς',
            ]
        }
    }

    assert expected == result


def test_dump_author_given_and_family_name_normal_case():
    data = {
        'name': {
            'value': 'Jones, Jessica',
        },
    }

    result = Author().dump(data).data
    expected = {
        'family_name': 'Jones',
        'given_name': 'Jessica',
    }

    assert expected == result


def test_dump_author_given_and_family_name_jimmy_case():
    data = {
        'name': {
            'value': 'Jimmy',
        },
    }

    result = Author().dump(data).data
    expected = {
        'given_name': 'Jimmy',
    }

    assert expected == result


def test_dump_author_given_and_family_name_multiple_names_case():
    data = {
        'name': {
            'value': 'Jones Castle, Jessica Frank',
        },
    }

    result = Author().dump(data).data
    expected = {
        'family_name': 'Jones Castle',
        'given_name': 'Jessica Frank',
    }

    assert expected == result


def test_load_author_given_and_family_name_normal_case():
    data = {
        'family_name': 'Jones',
        'given_name': 'Jessica',
    }

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'name': {
            'value': 'Jones, Jessica',
        },
    }

    assert expected == result


def test_load_author_given_and_family_name_jimmy_case():
    data = {
        'given_name': 'Jimmy',
    }

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'name': {
            'value': 'Jimmy',
        },
    }

    assert expected == result


def test_load_author_given_and_family_name_multiple_names_case():
    data = {
        'family_name': 'Jones Castle',
        'given_name': 'Jessica Frank',
    }

    result = Author().load(data).data
    expected = {
        '_collections': ['Authors'],
        'name': {
            'value': 'Jones Castle, Jessica Frank',
        },
    }

    assert expected == result


def test_dump_author_positions():
    data = {
        'positions': [
            {
                'institution': 'Colgate University',
                'start_date': '1994-02-01',
                'end_date': '1995-01-31',
                'rank': 'PHD',
                'current': False,
            },
        ],
    }

    result = Author().dump(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    expected = {
        'positions': [
            {
                'institution': 'Colgate University',
                'start_date': '1994-02-01',
                'end_date': '1995-01-31',
                'rank': 'PHD',
                'current': False,
            },
        ],
    }
    assert validate(data['positions'], subschema) is None
    assert expected == result


def test_load_author_positions():
    data = {
        'positions': [
            {
                'institution': 'Colgate University',
                'start_date': '1994-02-01',
                'end_date': '1995-01-31',
                'rank': 'PHD',
                'current': False,
            },
        ],
    }

    result = Author().load(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    expected = {
        '_collections': ['Authors'],
        'positions': [
            {
                'current': False,
                'curated_relation': False,
                'end_date': '1995-01-31',
                'institution': 'Colgate University',
                'rank': 'PHD',
                'start_date': '1994-02-01',
            },
        ],
    }

    assert validate(expected['positions'], subschema) is None
    assert expected == result


def test_dump_author_project_membership():
    data = {
        'project_membership': [
            {
                'institution': 'Colgate University',
                'start_date': '1994-02-01',
                'end_date': '1995-01-31',
                'rank': 'PHD',
                'current': False,
            },
        ],
    }

    result = Author().dump(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['positions']

    expected = {
        'project_membership': [
            {
                'institution': 'Colgate University',
                'start_date': '1994-02-01',
                'end_date': '1995-01-31',
                'rank': 'PHD',
                'current': False,
            },
        ],
    }
    assert validate(data['project_membership'], subschema) is None
    assert expected == result


def test_load_author_project_membership():
    data = {
        'project_membership': [
            {
                'name': 'pariatur',
                'start_date': '1997-05-01',
                'end_date': '2001-12-31',
                'record': {
                    '$ref': 'http://180'
                },
                'current': True
            }
        ],
    }

    result = Author().load(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['project_membership']

    expected = {
        '_collections': ['Authors'],
        'project_membership': [
            {
                'curated_relation': False,
                'current': True,
                'end_date': '2001-12-31',
                'name': 'pariatur',
                'record': {'$ref': 'http://180'},
                'start_date': '1997-05-01',
            },
        ],
    }

    assert validate(expected['project_membership'], subschema) is None
    assert expected == result


def test_dump_author_public_emails():
    data = {
        'email_addresses': [
            {
                'value': 'email@email.com',
            },
        ],
    }

    result = Author().dump(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    expected = {
        'public_emails': [
            'email@email.com',
        ],
    }
    assert validate(data['email_addresses'], subschema) is None
    assert expected == result


def test_load_author_public_emails():
    data = {
        'public_emails': [
            'email@email.com',
        ],
    }

    result = Author().load(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['email_addresses']

    expected = {
        '_collections': ['Authors'],
        'email_addresses': [
            {
                'value': 'email@email.com',
            },
        ],
    }

    assert validate(expected['email_addresses'], subschema) is None
    assert expected == result


def test_dump_author_status():
    data = {
        'status': 'active',
    }

    result = Author().dump(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['status']

    expected = {
        'status': 'active',
    }
    assert validate(data['status'], subschema) is None
    assert expected == result


def test_load_author_status():
    data = {
        'status': 'active',
    }

    result = Author().load(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['status']

    expected = {
        '_collections': ['Authors'],
        'status': 'active',
    }

    assert validate(expected['status'], subschema) is None
    assert expected == result


def test_dump_author_websites():
    data = {
        'urls': [
            {
                'value': 'http://website.com',
            },
        ],
    }

    result = Author().dump(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['urls']

    expected = {
        'websites': [
            'http://website.com',
        ],
    }
    assert validate(data['urls'], subschema) is None
    assert expected == result


def test_load_author_websites():
    data = {
        'websites': [
            'http://website.com',
        ],
    }

    result = Author().load(data).data
    schema = load_schema('authors')
    subschema = schema['properties']['urls']

    expected = {
        '_collections': ['Authors'],
        'urls': [
            {
                'value': 'http://website.com',
            },
        ],
    }

    assert validate(expected['urls'], subschema) is None
    assert expected == result
