# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Unit tests for the bibtex_booktitle helpers."""

import pytest

from invenio_records.api import Record

from inspirehep.utils.bibtex_booktitle import generate_booktitle, traverse


def test_generate_booktitle_no_publication_info():
    no_publication_info = Record({})

    expected = ''
    result = generate_booktitle(no_publication_info)

    assert expected == result


def test_generate_booktitle_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    expected = ''
    result = generate_booktitle(publication_info_an_empty_list)

    assert expected == result


def test_generate_booktitle_no_reportnumber():
    no_reportnumber = Record({
        'publication_info': [
            {}
        ]
    })

    expected = ''
    result = generate_booktitle(no_reportnumber)

    assert expected == result


def test_generate_booktitle_empty_reportnumber():
    empty_reportnumber = Record({
        'publication_info': [
            {
                'reportnumber': ''
            }
        ]
    })

    expected = ''
    result = generate_booktitle(empty_reportnumber)

    assert expected == result


@pytest.mark.xfail(reason='KeyError when looking for acronym')
def test_generate_booktitle_reportnumber_and_conf_acronym():
    recordnumber_and_conf_acronym = Record({
        'publication_info': [
            {
                'reportnumber': 'CERN-Proceedings-2010-001',
                'conf_acronym': 'FOO'  # No value in 773__o.
            }
        ]
    })

    expected = 'CERN-Proceedings-2010-0001: FOO'
    result = generate_booktitle(recordnumber_and_conf_acronym)

    assert expected == result


@pytest.mark.xfail(reason='KeyError when looking for acronym')
def test_generate_booktitle_reportnumber_but_no_conf_acronym():
    no_conf_acronym = Record({
        'publication_info': [
            {
                'reportnumber': 'CERN-Proceedings-2014-001'
            }
        ]
    })

    expected = ''
    result = generate_booktitle(no_conf_acronym)

    assert expected == result


def test_generate_booktitle_from_one_pubinfo_freetext():
    one_pubinfo_freetext = Record({
        'publication_info': [
            {
                'pubinfo_freetext': 'Adv. Theor. Math. Phys. 2 (1998) 51-59'
            }
        ]
    })

    expected = 'Adv. Theor. Math. Phys. 2 (1998) 51-59'
    result = generate_booktitle(one_pubinfo_freetext)

    assert expected == result


def test_generate_booktitle_from_two_pubinfo_freetext():
    two_pubinfo_freetext = Record({
        'publication_info': [
            {
                'pubinfo_freetext': 'Prog. Theor. Phys. 49 (1973) 652-657'
            },
            {
                'pubinfo_freetext': ('Also in *Lichtenberg, D. B. (Ed.), Rosen, S. P. '
                                     '(Ed.): Developments In The Quark Theory Of Hadrons'
                                     ', Vol. 1*, 218-223.')
            }
        ]
    })

    expected = ('Prog. Theor. Phys. 49 (1973) 652-657, Also in *Lichtenberg, D. B. (Ed.)'
                ', Rosen, S. P. (Ed.): Developments In The Quark Theory Of Hadrons, Vol.'
                ' 1*, 218-223.')
    result = generate_booktitle(two_pubinfo_freetext)

    assert expected == result


def test_traverse_yields_preorder():
    tree = [[1, 2], [3, 4], [5, [6]]]

    expected = [1, 2, 3, 4, 5, 6]
    result = list(traverse(tree))

    assert expected == result
