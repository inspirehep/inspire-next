# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import six

from inspirehep.modules.references.processors import (
    _split_refextract_authors_str, ReferenceBuilder)


def test_reference_builder_no_uids():
    rb = ReferenceBuilder()
    rb.set_number('oops')
    rb.set_number('1')
    rb.set_texkey('book')
    rb.add_title('Awesome Paper')
    rb.add_raw_reference('[1] Awesome Paper', 'arXiv')
    rb.add_misc('misc 0')
    rb.add_misc('misc 1')
    rb.add_author('Cox, Brian')
    rb.add_author('O Briain, Dara', 'ed.')
    rb.set_pubnote('Nucl.Phys.,B360,362')
    rb.set_pubnote('BAD PUBNOTE')
    rb.set_year('oops')
    rb.set_year('1991')
    rb.add_url('http://example.com')

    rb.set_publisher('Elsevier')
    rb.add_collaboration('ALICE')

    rb.add_report_number('hep-th/0603001')
    rb.add_report_number('hep-th/0603002')
    rb.add_report_number('arXiv:0705.0016 [hep-th]')
    rb.add_report_number('0705.0017 [hep-th]')
    rb.add_report_number('NOT ARXIV')

    expected = {
        "reference": {
            "texkey": "book",
            "collaboration": [
                "ALICE"
            ],
            "arxiv_eprints": [
                "hep-th/0603001",
                "hep-th/0603002",
                "0705.0016",
                "0705.0017"
            ],
            "misc": [
                "misc 0",
                "misc 1"
            ],
            "number": 1,
            "imprint": {
                "publisher": "Elsevier"
            },
            "titles": [
                {
                    "title": "Awesome Paper"
                }
            ],
            "urls": [
                {
                    "value": "http://example.com"
                }
            ],
            "authors": [
                {
                    "full_name": "Cox, Brian"
                },
                {
                    "role": "ed.",
                    "full_name": "O Briain, Dara"
                }
            ],
            "publication_info": {
                "journal_title": "Nucl.Phys.",
                "journal_volume": "B360",
                "reportnumber": "NOT ARXIV",
                "artid": "362",
                "year": 1991,
                "page_start": "362"
            }
        },
        "raw_refs": [
            {
                "source": "arXiv",
                "value": "[1] Awesome Paper",
                "schema": "text"
            },
            {
                "source": "reference_builder",
                "value": "BAD PUBNOTE",
                "schema": "text"
            }
        ]
    }

    assert expected == rb.obj


def test_curation():
    rb = ReferenceBuilder()
    rb.set_record({'$ref': 'http://example.com'})

    assert rb.obj == {'record': {'$ref': 'http://example.com'},
                      'curated_relation': False}

    rb.curate()
    assert rb.obj == {'record': {'$ref': 'http://example.com'},
                      'curated_relation': True}


def test_reference_builder_add_uid():
    rb = ReferenceBuilder()
    rb.add_uid(None)
    rb.add_uid('')
    rb.add_uid('thisisarandomstring')

    # arXiv eprint variations
    rb.add_uid('hep-th/0603001')
    rb.add_uid('0705.0017 [something-th]')
    # isbn
    rb.add_uid('1449344852')
    # cnum
    rb.add_uid('C87-11-11')
    # doi
    rb.add_uid('http://dx.doi.org/10.3972/water973.0145.db')
    # handle
    rb.add_uid('hdl:10443/1646')

    expected = {
        'reference': {
            'arxiv_eprints': ['hep-th/0603001', '0705.0017'],
            'publication_info': {
                'isbn': '978-1-4493-4485-6',
                'cnum': 'C87-11-11',
            },
            'dois': ['10.3972/water973.0145.db'],
            'persistent_identifiers': ['hdl:10443/1646']
        }
    }

    assert expected == rb.obj


def test_refextract_authors():
    author_strings = [
        'Butler, D., Demarque, P., & Smith, H. A.',
        'Cenko, S. B., Kasliwal, M. M., Perley, D. A., et al.',
        'J. Kätlne et al.',  # Also test some unicode cases.
        u'J. Kätlne et al.',
        'Hoaglin D. C., Mostellar F., Tukey J. W.',
        'V.M. Zhuravlev, S.V. Chervon, and V.K. Shchigolev',
        'Gómez R, Reilly P, Winicour J and Isaacson R'
    ]

    expected = [
        ['Butler, D.', 'Demarque, P.', 'Smith, H. A.'],
        ['Cenko, S. B.', 'Kasliwal, M. M.', 'Perley, D. A.'],
        ['J. Kätlne'],
        ['J. Kätlne'],
        ['Hoaglin D. C.', 'Mostellar F.', 'Tukey J. W.'],
        ['V.M. Zhuravlev', 'S.V. Chervon', 'V.K. Shchigolev'],
        ['Gómez R', 'Reilly P', 'Winicour J', 'Isaacson R']
    ]

    for idx, authors_str in enumerate(author_strings):
        # Expect that the function returns correct unicode representations.
        expected_authors = [six.text_type(e.decode('utf8'))
                            for e in expected[idx]]
        assert _split_refextract_authors_str(authors_str) == expected_authors
