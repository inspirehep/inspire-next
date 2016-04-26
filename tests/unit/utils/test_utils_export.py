# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for Export, the base class of exporters."""

import mock

from invenio_records.api import Record

from inspirehep.utils.export import Export


def test_get_citation_key_no_external_system_numbers():
    no_external_system_numbers = Record({})

    expected = ''
    result = Export(no_external_system_numbers)._get_citation_key()

    assert expected == result


def test_get_citation_key_with_external_system_numbers_from_value():
    with_external_system_numbers_from_value = Record({
        'external_system_numbers': [
            {'institute': 'INSPIRETeX', 'value': 'foo'}
        ]
    })

    expected = 'foo'
    result = Export(with_external_system_numbers_from_value)._get_citation_key()

    assert expected == result


def test_get_citation_key_no_value_no_obsolete():
    from inspirehep.utils.export import Export

    no_value_no_obsolete = Record({
        'external_system_numbers': [
            {'institute': 'INSPIRETeX'}
        ]
    })

    expected = ''
    result = Export(no_value_no_obsolete)._get_citation_key()

    assert expected == result


def test_get_citation_key_last_one_wins():

    last_one_wins = Record({
        'external_system_numbers': [
            {'institute': 'INSPIRETeX', 'value': 'foo'},
            {'institute': 'SPIRESTeX', 'value': 'bar'},
        ]
    })

    expected = 'bar'
    result = Export(last_one_wins)._get_citation_key()

    assert expected == result


def test_get_citation_key_a_list_selects_first():
    a_list_selects_first = Record({
        'external_system_numbers': [
            {
                'institute': 'INSPIRETeX',
                'value': ['foo', 'bar']
            }
        ]
    })

    expected = 'foo'
    result = Export(a_list_selects_first)._get_citation_key()

    assert expected == result


def test_get_citation_key_trims_spaces():
    trims_spaces = Record({
        'external_system_numbers': [
            {'institute': 'INSPIRETeX', 'value': 'f o o'}
        ]
    })

    expected = 'foo'
    result = Export(trims_spaces)._get_citation_key()

    assert expected == result


def test_get_doi_no_dois():
    no_dois = Record({})

    expected = ''
    result = Export(no_dois)._get_doi()

    assert expected == result


def test_get_doi_single_doi():
    single_doi = Record({
        'dois': [
            {'value': 'foo'}
        ]
    })

    expected = 'foo'
    result = Export(single_doi)._get_doi()

    assert expected == result


def test_get_doi_multiple_dois():

    multiple_dois = Record({
        'dois': [
            {'value': 'foo'},
            {'value': 'bar'}
        ]
    })

    expected = 'foo, bar'
    result = Export(multiple_dois)._get_doi()

    assert expected == result


def test_get_doi_removes_duplicates():

    with_duplicates = Record({
        'dois': [
            {'value': 'foo'},
            {'value': 'bar'},
            {'value': 'foo'}
        ]
    })

    expected = 'foo, bar'
    result = Export(with_duplicates)._get_doi()

    assert expected == result


def test_arxiv_field_no_arxiv_eprints():
    no_arxiv_eprints = Record({})

    result = Export(no_arxiv_eprints).arxiv_field

    assert result is None


def test_arxiv_field_single_arxiv_eprints():
    single_arxiv_eprints = Record({
        'arxiv_eprints': [
            {'value': 'foo'}
        ]
    })

    expected = {'value': 'foo'}
    result = Export(single_arxiv_eprints).arxiv_field

    assert expected == result


def test_arxiv_field_returns_first():
    returns_first = Record({
        'arxiv_eprints': [
            {'value': 'foo'},
            {'value': 'bar'}
        ]
    })

    expected = {'value': 'foo'}
    result = Export(returns_first).arxiv_field

    assert expected == result


def test_get_arxiv_no_arxiv_eprints():
    no_arxiv_eprints = Record({})

    expected = ''
    result = Export(no_arxiv_eprints)._get_arxiv()

    assert expected == result


def test_get_arxiv_no_value():
    no_value = Record({
        'arxiv_eprints': [
            {'notvalue': 'foo'}
        ]
    })

    expected = ''
    result = Export(no_value)._get_arxiv()

    assert expected == result


def test_get_arxiv_value_no_categories():
    value_no_categories = Record({
        'arxiv_eprints': [
            {'value': 'foo'}
        ]
    })

    expected = 'foo'
    result = Export(value_no_categories)._get_arxiv()

    assert expected == result


def test_get_arxiv_single_category():

    single_category = Record({
        'arxiv_eprints': [
            {
                'value': 'foo',
                'categories': ['bar']
            }
        ]
    })

    expected = 'foo [bar]'
    result = Export(single_category)._get_arxiv()

    assert expected == result


def test_get_arxiv_multiple_categories():

    multiple_categories = Record({
        'arxiv_eprints': [
            {
                'value': 'foo',
                'categories': [
                    'bar',
                    'baz'
                ]
            }
        ]
    })

    expected = 'foo [bar,baz]'
    result = Export(multiple_categories)._get_arxiv()

    assert expected == result


def test_get_report_number_no_report_numbers():

    no_report_numbers = Record({})

    expected = []
    result = Export(no_report_numbers)._get_report_number()

    assert expected == result


def test_get_report_number_no_value():

    no_value = Record({
        'report_numbers': [
            {'notvalue': 'foo'}
        ]
    })

    expected = ''
    result = Export(no_value)._get_report_number()

    assert expected == result


def test_get_report_number_single_value():

    single_value = Record({
        'report_numbers': [
            {'value': 'foo'}
        ]
    })

    expected = 'foo'
    result = Export(single_value)._get_report_number()

    assert expected == result


def test_get_report_number_multiple_values():

    multiple_values = Record({
        'report_numbers': [
            {'value': 'foo'},
            {'value': 'bar'}
        ]
    })

    expected = 'foo, bar'
    result = Export(multiple_values)._get_report_number()

    assert expected == result


def test_get_slac_citation_from_arxiv_eprints_no_value():

    from_arxiv_eprints_no_value = Record({
        'arxiv_eprints': [
            {'notvalue': 'foo'}
        ]
    })

    expected = ''
    result = Export(from_arxiv_eprints_no_value)._get_slac_citation()

    assert expected == result

def test_get_slac_citation_from_arxiv_eprints_with_value():

    from_arxiv_eprints_with_value = Record({
        'arxiv_eprints': [
            {'value': 'foo'}
        ]
    })

    expected = '%%CITATION = FOO;%%'
    result = Export(from_arxiv_eprints_with_value)._get_slac_citation()

    assert expected == result


def test_get_slac_citation_from_pubnote():
    # XXX(jacquerie): stubbing _get_pubnote because it is implemented
    #                 by subclasses of Export.
    Export._get_pubnote = lambda self: 'foo'

    from_pubnote = Record({})

    expected = '%%CITATION = foo;%%'
    result = Export(from_pubnote)._get_slac_citation()

    assert expected == result

    del Export._get_pubnote


def test_get_slac_citation_from_report_numbers_no_arxiv_eprints():
    # XXX(jacquerie): stubbing _get_pubnote because it is implemented
    #                 by subclasses of Export.
    Export._get_pubnote = lambda self: False

    from_report_numbers_no_arxiv_eprints = Record({
        'report_numbers': [
            {'value': 'foo'},
            {'value': 'bar'}
        ]
    })

    expected = '%%CITATION = FOO;%%'
    result = Export(from_report_numbers_no_arxiv_eprints)._get_slac_citation()

    assert expected == result

    del Export._get_pubnote


def test_get_slac_citation_from_control_number():
    # XXX(jacquerie): stubbing _get_pubnote because it is implemented
    #                 by subclasses of Export.
    Export._get_pubnote = lambda self: False

    from_recid = Record({'control_number': 1})

    expected = '%%CITATION = INSPIRE-1;%%'
    result = Export(from_recid)._get_slac_citation()

    assert expected == result

    del Export._get_pubnote


@mock.patch('inspirehep.utils.export.get_es_record')
def test_get_citation_number_no_citations(g_e_r):
    g_e_r.return_value = {'citation_count': 0}

    no_citations = Record({'control_number': 1})

    expected = ''
    result = Export(no_citations)._get_citation_number()

    assert expected == result


@mock.patch('inspirehep.utils.export.time.strftime')
@mock.patch('inspirehep.utils.export.get_es_record')
def test_get_citation_number_one_citation(g_e_r, strftime):
    strftime.return_value = '02 Feb 1993'
    g_e_r.return_value = {'citation_count': 1}

    one_citation = Record({'control_number': 1})

    expected = '1 citation counted in INSPIRE as of 02 Feb 1993'
    result = Export(one_citation)._get_citation_number()

    assert expected == result


@mock.patch('inspirehep.utils.export.time.strftime')
@mock.patch('inspirehep.utils.export.get_es_record')
def test_get_citation_number_two_citations(g_e_r, strftime):
    strftime.return_value = '02 Feb 1993'
    g_e_r.return_value = {'citation_count': 2}

    two_citations = Record({'control_number': 1})

    expected = '2 citations counted in INSPIRE as of 02 Feb 1993'
    result = Export(two_citations)._get_citation_number()

    assert expected == result


@mock.patch('inspirehep.utils.export.get_es_record')
def test_get_citation_number_no_citation_count(g_e_r):
    g_e_r.return_value = {}

    no_citation_count = Record({'control_number': 1})

    expected = ''
    result = Export(no_citation_count)._get_citation_number()

    assert expected == result
