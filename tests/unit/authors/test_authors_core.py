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

from inspirehep.modules.authors.core import convert_for_form


def test_convert_for_form_without_name_urls_fc_positions_advisors_and_ids():
    without_name_urls_fc_positions_advisors_and_ids = {}
    convert_for_form(without_name_urls_fc_positions_advisors_and_ids)

    assert {} == without_name_urls_fc_positions_advisors_and_ids


def test_convert_for_form_advisors():
    record = {
        'advisors': [
            {
                'degree_type': 'other',
                'name': 'Avignone, Frank T.',
                'curated_relation': False
            }
        ]
    }
    convert_for_form(record)

    expected = [
        {
            'degree_type': 'other',
            'name': 'Avignone, Frank T.'
        }
    ]

    assert expected == record['advisors']


def test_convert_for_form_ids():
    record = {
        'ids': [
            {
                'schema': 'ORCID',
                'value': '0000-0001-7761-7242'
            },
            {
                'schema': 'INSPIRE BAI',
                'value': 'Takeshi.Furukawa.1'
            },
            {
                'schema': 'INSPIRE ID',
                'value': 'INSPIRE-00086433'
            }
        ]
    }

    convert_for_form(record)

    expected_record = {
        'ids': [
            {
                'schema': 'ORCID',
                'value': '0000-0001-7761-7242'
            },
            {
                'schema': 'INSPIRE BAI',
                'value': 'Takeshi.Furukawa.1'
            },
            {
                'schema': 'INSPIRE ID',
                'value': 'INSPIRE-00086433'
            }
        ],
        'orcid': '0000-0001-7761-7242',
        'bai': 'Takeshi.Furukawa.1',
        'inspireid': 'INSPIRE-00086433'
    }

    assert expected_record == record


def test_convert_for_form_institution_history_and_public_emails():
    record = {
        'positions': [
            {
                'emails': [
                    'michael.abbott@uct.ac.za',
                ],
                'institution': {'name': 'Tokyo Metropolitan U.'},
                '_rank': 'JUNIOR',
                'start_date': '2010',
                'end_date': '2011',
                'current': True,
                'old_emails': [
                    'oldemail1@exmaple.com',
                    'oldemail2@exmaple.com'
                ]
            },
            {
                'emails': [
                    'abbott@theory.tifr.res.in'
                ],
                'institution': {'name': 'Manchester Metropolitan University'},
                '_rank': 'SENIOR',
            },
            {
                'old_emails': [
                    'abbott@het.brown.edu'
                ]
            }
        ]
    }

    convert_for_form(record)

    expected_public_emails = [
        {
            'email': 'michael.abbott@uct.ac.za',
            'original_email': 'michael.abbott@uct.ac.za'
        },
        {
            'email': 'abbott@theory.tifr.res.in',
            'original_email': 'abbott@theory.tifr.res.in'
        }
    ]

    expected_institution_history = [
        {
            'name': 'Manchester Metropolitan University',
            'rank': 'SENIOR',
            'current': False,
            'old_emails': [],
            'emails': [
                'abbott@theory.tifr.res.in'
            ],
        },
        {
            'name': 'Tokyo Metropolitan U.',
            'rank': 'JUNIOR',
            'start_year': 2010,
            'end_year': 2011,
            'current': True,
            'old_emails': [
                'oldemail1@exmaple.com',
                'oldemail2@exmaple.com'
            ],
            'emails': [
                'michael.abbott@uct.ac.za',
            ],
        }
    ]

    assert expected_public_emails == record['public_emails']
    assert expected_institution_history == record['institution_history']


def test_convert_for_form_public_emails_only():
    current_and_old_emails = {
        'positions': [
            {
                'emails': [
                    'michael.abbott@uct.ac.za'
                ]
            },
            {
                'emails': [
                    'abbott@theory.tifr.res.in'
                ]
            },
            {
                'old_emails': [
                    'abbott@het.brown.edu'
                ]
            }
        ]
    }
    convert_for_form(current_and_old_emails)

    expected = [
        {
            'email': 'michael.abbott@uct.ac.za',
            'original_email': 'michael.abbott@uct.ac.za'
        },
        {
            'email': 'abbott@theory.tifr.res.in',
            'original_email': 'abbott@theory.tifr.res.in'
        }
    ]

    assert expected == current_and_old_emails['public_emails']


def test_convert_for_form_names():
    record = {
        'name': {
            'value': 'Lusignoli, Maurizio',
            'preferred_name': 'Maurizio Musignoli'
        },
        'native_name': [
            'Lusignoli, Maurizzio',
            'LLusignoli, Maurizo'
        ]
    }

    convert_for_form(record)

    expected_record = {
        'name': {
            'value': 'Lusignoli, Maurizio',
            'preferred_name': 'Maurizio Musignoli'
        },
        'full_name': 'Lusignoli, Maurizio',
        'given_names': 'Maurizio',
        'family_name': 'Lusignoli',
        'display_name': 'Maurizio Musignoli',
        'native_name': 'Lusignoli, Maurizzio'
    }

    assert expected_record == record


def test_convert_for_form_research_field():
    record = {
        'arxiv_categories': [
            'astro-ph',
            'hep-ex',
            'hep-ph'
        ]
    }

    convert_for_form(record)

    expected_research_field = [
        'astro-ph',
        'hep-ex',
        'hep-ph'
    ]

    assert expected_research_field == record['research_field']


def test_convert_for_form_urls():
    record = {
        'urls': [
            {
                'value': 'http://example.com'
            },
            {
                'description': 'TWITTER',
                'value': 'http://twitter.com'
            },
            {
                'description': 'BLOG',
                'value': 'http://blog.com'
            },
            {
                'description': 'LINKEDIN',
                'value': 'http://linkedin.com'
            }
        ],
    }

    convert_for_form(record)

    expected_record = {
        'websites': [
            {'webpage': 'http://example.com'}
        ],
        'twitter_url': 'http://twitter.com',
        'blog_url': 'http://blog.com',
        'linkedin_url': 'http://linkedin.com'
    }

    assert expected_record == record
