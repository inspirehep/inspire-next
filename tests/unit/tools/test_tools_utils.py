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

from inspirehep.modules.tools.utils import authorlist


def test_authorlist_affiliation_with_utf8_character():
    text = (
        'C. Patrignani1 K. Agashe2 G. Aielli1,2\n'
        '\n'
        '1 Universit`a di Bologna and INFN, Italy\n'
        '2 University of Maryland, MD 20742-4111, USA'
    )

    expected = [
        {
            'full_name': u'Patrignani, C.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Italy'},
            ],
        },
        {
            'full_name': u'Agashe, K.',
            'raw_affiliations': [
                {'value': u'University of Maryland, MD 20742-4111, USA'},
            ],
        },
        {
            'full_name': u'Aielli, G.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Italy'},
                {'value': u'University of Maryland, MD 20742-4111, USA'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']
    assert 'warnings' not in result.keys()


def test_authorlist_with_warning():
    text = (
        'Y.X. Ali1,* 20, E I Andronov20\n'
        '\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = [
        {
            'full_name': u'Ali, Y.X.',
            'raw_affiliations': [
                {'value': u'CERN'},
                {'value': u'DESY'},
            ],
        },
        {
            'full_name': u'Andronov, E.I.',
            'raw_affiliations': [
                {'value': u'DESY'},
            ],
        },
    ]

    result = authorlist(text)

    assert expected == result['authors']
    assert 'Unresolved aff-ID or stray footnote symbol' in result['warnings'][0]
