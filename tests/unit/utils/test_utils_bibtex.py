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

"""Unit tests for the BibTeX exporter."""

import mock
import pytest

from inspirehep.utils.bibtex import Bibtex
from invenio_records.api import Record


def test_get_entry_type_no_collections_no_pubinfo():
    no_collections_no_pubinfo = Record({})

    expected = ('article', 'article')
    result = Bibtex(no_collections_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_no_primary_collections_no_pubinfo():
    no_primary_collections_no_pubinfo = Record({
        'collections': [
            {'not-primary': 'foo'}
        ]
    })

    expected = ('article', 'article')
    result = Bibtex(no_primary_collections_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_conferencepaper_no_pubinfo():
    conferencepaper_no_pubinfo = Record({
        'collections': [
            {'primary': 'conferencepaper'}
        ]
    })

    expected = ('inproceedings', 'inproceedings')
    result = Bibtex(conferencepaper_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_thesis_no_pubinfo():
    thesis_no_pubinfo = Record({
        'collections': [
            {'primary': 'thesis'}
        ]
    })

    expected = ('thesis', 'thesis')
    result = Bibtex(thesis_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_proceedings_no_pubinfo():
    proceedings_no_pubinfo = Record({
        'collections': [
            {'primary': 'proceedings'}
        ]
    })

    expected = ('proceedings', 'proceedings')
    result = Bibtex(proceedings_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_book_no_pubinfo():
    book_no_pubinfo = Record({
        'collections': [
            {'primary': 'book'}
        ]
    })

    expected = ('book', 'book')
    result = Bibtex(book_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_bookchapter_no_pubinfo():
    bookchapter_no_pubinfo = Record({
        'collections': [
            {'primary': 'bookchapter'}
        ]
    })

    expected = ('inbook', 'inbook')
    result = Bibtex(bookchapter_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_arxiv_no_pubinfo():
    arxiv_no_pubinfo = Record({
        'collections': [
            {'primary': 'arxiv'}
        ]
    })

    expected = ('article', 'article')
    result = Bibtex(arxiv_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_published_no_pubinfo():
    published_no_pubinfo = Record({
        'collections': [
            {'primary': 'published'}
        ]
    })

    expected = ('article', 'article')
    result = Bibtex(published_no_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_no_collections_one_valid_pubinfo():
    no_collections_one_valid_pubinfo = Record({
        'publication_info': {
            'journal_title': 'foo',
            'journal_volume': 'bar',
            'page_start': 'baz',
            'year': 'quux'
        }
    })

    expected = ('article', 'article')
    result = Bibtex(no_collections_one_valid_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_no_collections_one_invalid_pubinfo():
    no_collections_one_invalid_pubinfo = Record({
        'publication_info': {}
    })

    expected = ('article', 'article')
    result = Bibtex(no_collections_one_invalid_pubinfo)._get_entry_type()

    assert expected == result


def test_get_entry_type_no_collections_second_pubinfo_valid():
    no_collections_second_pubinfo_valid = Record({
        'publication_info': [
            {},
            {
                'journal_title': 'foo',
                'journal_volume': 'bar',
                'page_start': 'baz',
                'year': 'quux'
            }
        ]
    })

    expected = ('article', 'article')
    result = Bibtex(no_collections_second_pubinfo_valid)._get_entry_type()

    assert expected == result


def test_get_entry_type_one_collection_one_pubinfo():
    one_collection_one_pubinfo = Record({
        'collections': [{'primary': 'conferencepaper'}],
        'publication_info': [
            {
                'journal_title': 'foo',
                'journal_volume': 'bar',
                'page_start': 'baz',
                'year': 'quux'
            }
        ]
    })

    expected = ('article', 'inproceedings')
    result = Bibtex(one_collection_one_pubinfo)._get_entry_type()

    assert expected == result


@pytest.mark.xfail
@mock.patch('inspirehep.utils.bibtex.Bibtex._get_key')
def test_fetch_fields_missing_required_key(self, _get_key):
    _get_key.return_value = None

    from inspirehep.utils.export import MissingRequiredFieldError

    dummy = Record({})

    with pytest.raises(MissingRequiredFieldError) as excinfo:
        Bibtex(dummy)._fetch_fields(['key'], [])
    assert 'key' in str(excinfo.value)


def test_format_output_row_single_author():
    dummy = Record({})

    expected = u'      author         = "0",\n'
    result = Bibtex(dummy)._format_output_row('author', [0])

    assert expected == result


def test_format_output_row_between_one_and_ten_authors():
    dummy = Record({})

    expected = u'      author         = "0 and 1 and 2",\n'
    result = Bibtex(dummy)._format_output_row('author', list(range(3)))

    assert expected == result


def test_format_output_row_more_than_ten_authors():
    dummy = Record({})

    expected = u'      author         = "0 and others",\n'
    result = Bibtex(dummy)._format_output_row('author', list(range(11)))

    assert expected == result


def test_format_output_row_title():
    dummy = Record({})

    expected = u'      title          = "{bar}",\n'
    result = Bibtex(dummy)._format_output_row('title', 'bar')

    assert expected == result


def test_format_output_row_doi():
    dummy = Record({})

    expected = u'      doi            = "bar",\n'
    result = Bibtex(dummy)._format_output_row('doi', 'bar')

    assert expected == result


def test_format_output_row_slaccitation():
    dummy = Record({})

    expected = u'      SLACcitation   = "bar"'
    result = Bibtex(dummy)._format_output_row('SLACcitation', 'bar')

    assert expected == result


def test_format_output_row_number_value():
    dummy = Record({})

    expected = u'      foo            = "0",\n'
    result = Bibtex(dummy)._format_output_row('foo', 0)

    assert expected == result


def test_format_output_row_not_number_value():
    dummy = Record({})

    expected = u'      foo            = "bar",\n'
    result = Bibtex(dummy)._format_output_row('foo', 'bar')

    assert expected == result


def test_is_number():
    dummy = Record({})

    assert Bibtex(dummy)._is_number(0)
    assert not Bibtex(dummy)._is_number('foo')


@mock.patch('inspirehep.utils.export.Export._get_citation_key')
def test_get_key_empty(_g_c_k):
    _g_c_k.return_value = True

    dummy = Record({})

    expected = ''
    result = Bibtex(dummy)._get_key()

    assert expected == result


@mock.patch('inspirehep.utils.export.Export._get_citation_key')
def test_get_key_from_control_number(_g_c_k):
    _g_c_k.return_value = False

    with_control_number = Record({'control_number': '1'})

    expected = '1'
    result = Bibtex(with_control_number)._get_key()

    assert expected == result


def test_get_author_no_authors_no_corporate_author():
    no_authors_no_corporate_author = Record({})

    expected = []
    result = Bibtex(no_authors_no_corporate_author)._get_author()

    assert expected == result


def test_get_author_one_author_without_full_name():
    one_author_without_full_name = Record({
        'authors': [{}]
    })

    expected = []
    result = Bibtex(one_author_without_full_name)._get_author()

    assert expected == result


def test_get_author_one_author_with_full_name_a_list():
    one_author_with_full_name_a_list = Record({
        'authors': [
            {
                'full_name': [
                    'Goldstone, Jeffrey',
                    'Salam, Abdus',
                    'Weinberg, Steven'
                ]
            }
        ]
    })

    expected = ['Goldstone, Jeffreyand Salam, Abdusand Weinberg, Steven']
    result = Bibtex(one_author_with_full_name_a_list)._get_author()

    assert expected == result


def test_get_author_one_author_with_one_fullname():
    one_author_with_one_fullname = Record({
        'authors': [
            {'full_name': 'Higgs, Peter W.'}
        ]
    })

    expected = ['Higgs, Peter W.']
    result = Bibtex(one_author_with_one_fullname)._get_author()

    assert expected == result


def test_get_author_two_authors_with_fullnames():
    two_authors_with_fullnames = Record({
        'authors': [
            {'full_name': 'Englert, F.'},
            {'full_name': 'Brout, R.'}
        ]
    })

    expected = ['Englert, F.', 'Brout, R.']
    result = Bibtex(two_authors_with_fullnames)._get_author()

    assert expected == result


def test_get_author_corporate_author():
    corporate_author = Record({
        'corporate_author': [
            'CMS Collaboration'
        ]
    })

    expected = ['CMS Collaboration']
    result = Bibtex(corporate_author)._get_author()

    assert expected == result


def test_get_editor_no_authors():
    no_authors = Record({})

    assert Bibtex(no_authors)._get_editor() is None


def test_get_editor_no_author_has_editor_role():
    no_author_has_editor_role = Record({
        'authors': [
            {'full_name': 'Englert, F.'},
            {'full_name': 'Brout, R.'}
        ]
    })

    assert Bibtex(no_author_has_editor_role)._get_editor() is None


def test_get_editor_first_author_has_editor_role():
    first_author_has_editor_role = Record({
        'authors': [
            {
                'full_name': 'Englert, F.',
                'role': 'ed.'
            },
            {'full_name': 'Brout, R.'}
        ]
    })

    expected = 'Englert, F.'
    result = Bibtex(first_author_has_editor_role)._get_editor()

    assert expected == result


def test_get_editor_non_first_author_has_editor_role():
    non_first_author_has_editor_role = Record({
        'authors': [
            {'full_name': 'Englert, F.'},
            {
                'full_name': 'Brout, R.',
                'role': 'ed.'
            }
        ]
    })

    assert Bibtex(non_first_author_has_editor_role)._get_editor() is None


def test_get_title_no_titles():
    no_titles = Record({})

    expected = ''
    result = Bibtex(no_titles)._get_title()

    assert expected == result


def test_get_title_one_title():
    one_title = Record({
        'titles': {
            'title': 'Partial Symmetries of Weak Interactions'
        }
    })

    expected = 'Partial Symmetries of Weak Interactions'
    result = Bibtex(one_title)._get_title()

    assert expected == result


def test_get_title_with_a_list_of_titles_selectes_first():
    a_list_of_titles = Record({
        'titles': [
            {'title': 'Broken Symmetries and the Masses of Gauge Bosons'},
            {'title': 'BROKEN SYMMETRIES AND THE MASSES OF GAUGE BOSONS.'}
        ]
    })

    expected = 'Broken Symmetries and the Masses of Gauge Bosons'
    result = Bibtex(a_list_of_titles)._get_title()

    assert expected == result


def test_get_collaboration_no_collaboration():
    no_collaboration = Record({})

    expected = ''
    result = Bibtex(no_collaboration)._get_collaboration()

    assert expected == result


def test_get_collaboration_with_a_list_of_collaboration_selects_first():
    a_list_of_collaboration = Record({
        'collaboration': [
            {'value': 'ATLAS'},
            {'value': 'CMS'}
        ]
    })

    expected = 'ATLAS'
    result = Bibtex(a_list_of_collaboration)._get_collaboration()

    assert expected == result


def test_get_collaboration_malformed_collaboration():
    malformed_collaboration = Record({
        'collaboration': [
            {'notvalue': 'ATLAS'}
        ]
    })

    expected = ''
    result = Bibtex(malformed_collaboration)._get_collaboration()

    assert expected == result


def test_get_organization_no_imprints():
    no_imprints = Record({})

    expected = ''
    result = Bibtex(no_imprints)._get_organization()

    assert expected == result


def test_get_organization_with_a_list_of_imprints_selects_first_with_a_publisher():
    a_list_of_imprints_with_a_publisher = Record({
        'imprints': [
            {},
            {'publisher': 'Cambridge University Press'}
        ]
    })

    expected = 'Cambridge University Press'
    result = Bibtex(a_list_of_imprints_with_a_publisher)._get_organization()

    assert expected == result


def test_get_address_no_imprints():
    no_imprints = Record({})

    expected = []
    result = Bibtex(no_imprints)._get_address()

    assert expected == result


def test_get_address_a_list_of_imprints_with_no_places():
    a_list_of_imprints_with_no_places = Record({
        'imprints': [
            {'notplace': 'Piscataway, USA'}
        ]
    })

    assert Bibtex(a_list_of_imprints_with_no_places)._get_address() is None


def test_get_address_a_list_of_imprints_with_one_place_not_a_list():
    a_list_of_imprints_with_one_place_not_a_list = Record({
        'imprints': [
            {'place': 'Piscataway, USA'}
        ]
    })

    expected = 'Piscataway, USA'
    result = Bibtex(a_list_of_imprints_with_one_place_not_a_list)._get_address()

    assert expected == result


def test_get_address_a_list_of_imprints_with_one_place_a_list():
    a_list_of_imprints_with_one_place_a_list = Record({
        'imprints': [
            {
                'place': [
                    'Moscow',
                    'Russia'
                ]
            }
        ]
    })

    expected = 'Moscow'
    result = Bibtex(a_list_of_imprints_with_one_place_a_list)._get_address()

    assert expected == result


def test_get_address_a_list_of_imprints_with_two_places():
    a_list_of_imprints_with_two_places = Record({
        'imprints': [
            {'place': 'Moscow'},
            {'place': 'Russia'}
        ]
    })

    expected = 'Moscow'
    result = Bibtex(a_list_of_imprints_with_two_places)._get_address()

    assert expected == result


def test_get_school_no_authors():
    no_authors = Record({})

    expected = ''
    result = Bibtex(no_authors)._get_school()

    assert expected == result


def test_get_school_a_list_of_authors_with_no_affiliations():
    a_list_of_authors_with_no_affiliations = Record({'authors': []})

    expected = ''
    result = Bibtex(a_list_of_authors_with_no_affiliations)._get_school()

    assert expected == result


def test_get_school_a_list_of_authors_with_one_affiliation_each():
    a_list_of_authors_with_one_affiliation_each = Record({
        'authors': [
            {
                'affiliations': [
                    {'value': 'Copenhagen U.'}
                ]
            },
            {
                'affiliations': [
                    {'value': 'Edinburgh U.'}
                ]
            }
        ]
    })

    expected = 'Edinburgh U.'
    result = Bibtex(a_list_of_authors_with_one_affiliation_each)._get_school()

    assert expected == result


def test_get_school_a_list_of_authors_with_more_than_one_affiliation_each():
    a_list_of_authors_with_more_than_one_affiliation_each = Record({
        'authors': [
            {
                'affiliations': [
                    {'value': 'Warsaw U.'},
                    {'value': 'Madrid, Inst. Estructura Materia'}
                ]
            },
            {
                'affiliations': [
                    {'value': 'Potsdam, Max Planck Inst.'},
                    {'value': 'Perimeter Inst. Theor. Phys.'}
                ]
            }
        ]
    })

    expected = 'Potsdam, Max Planck Inst.'
    result = Bibtex(a_list_of_authors_with_more_than_one_affiliation_each)._get_school()

    assert expected == result


def test_get_booktitle_not_in_proceedings():
    record = Record({})

    not_in_proceedings = Bibtex(record)
    not_in_proceedings.entry_type = 'not-inproceedings'
    not_in_proceedings.original_entry = 'not-inproceedings'

    assert not_in_proceedings._get_booktitle() is None


@mock.patch('inspirehep.utils.bibtex.bibtex_booktitle.generate_booktitle')
def test_get_booktitle_from_generate_booktitle(g_b):
    # TODO: mock the actual generate_booktitle output.
    g_b.return_value = 'foo bar baz'

    record = Record({})

    in_proceedings = Bibtex(record)
    in_proceedings.entry_type = 'inproceedings'

    expected = '{foo bar baz}'
    result = in_proceedings._get_booktitle()

    assert expected == result


def test_get_year_no_publication_info_no_thesis_no_imprints_no_preprint_date():
    no_publication_info_no_thesis_no_imprints_no_preprint_date = Record({})

    expected = ''
    result = Bibtex(no_publication_info_no_thesis_no_imprints_no_preprint_date)._get_year()

    assert expected == result


def test_get_year_from_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    expected = ''
    result = Bibtex(publication_info_an_empty_list)._get_year()

    assert expected == result


def test_get_year_from_publication_info_a_list_one_year():
    publication_info_a_list_one_year = Record({
        'publication_info': [
            {'year': '2015'}
        ]
    })

    expected = '2015'
    result = Bibtex(publication_info_a_list_one_year)._get_year()

    assert expected == result


def test_get_year_from_publication_info_a_list_from_imprints():
    publication_info_a_list_from_imprints = Record({
        'publication_info': [],
        'imprints': [
            {'date': '2015-12-04'}
        ]
    })

    expected = '2015'
    result = Bibtex(publication_info_a_list_from_imprints)._get_year()

    assert expected == result


def test_get_year_from_publication_info_a_list_from_preprint_date():
    publication_info_a_list_from_preprint_date = Record({
        'publication_info': [],
        'preprint_date': [
            '2015-12-04'
        ]
    })

    expected = '2015'
    result = Bibtex(publication_info_a_list_from_preprint_date)._get_year()

    assert expected == result


def test_get_year_from_thesis_an_empty_obj():
    record = Record({
        'thesis': {}
    })

    thesis_an_empty_list = Bibtex(record)
    thesis_an_empty_list.original_entry = 'thesis'

    expected = ''
    result = thesis_an_empty_list._get_year()

    assert expected == result


def test_get_year_from_thesis_an_empty_obj_but_preprint_date():
    record = Record({
        'preprint_date': '1998-04-30',
        'thesis': {}
    })

    thesis_an_empty_list_but_preprint_date = Bibtex(record)
    thesis_an_empty_list_but_preprint_date.original_entry = 'thesis'

    expected = '1998'
    result = thesis_an_empty_list_but_preprint_date._get_year()

    assert expected == result


def test_get_year_from_thesis_an_empty_obj_but_imprints():
    record = Record({
        'imprints': [{'date': '2015-12-04'}],
        'thesis': {}
    })

    thesis_an_empty_list_but_imprints = Bibtex(record)
    thesis_an_empty_list_but_imprints.original_entry = 'thesis'

    expected = '2015'
    result = thesis_an_empty_list_but_imprints._get_year()

    assert expected == result


def test_get_year_from_thesis_one_date():
    record = Record({
        'thesis': {'date': '2008'}
    })

    thesis_one_date = Bibtex(record)
    thesis_one_date.original_entry = 'thesis'

    expected = '2008'
    result = thesis_one_date._get_year()

    assert expected == result


def test_get_year_from_imprints_an_empty_list():
    imprints_an_empty_list = Record({
        'imprints': []
    })

    expected = ''
    result = Bibtex(imprints_an_empty_list)._get_year()

    assert expected == result


def test_get_year_from_imprints_one_date():
    imprints_one_date = Record({
        'imprints': [
            {'date': '1998-04-30'}
        ]
    })

    expected = '1998'
    result = Bibtex(imprints_one_date)._get_year()

    assert expected == result


def test_get_year_from_imprints_two_dates():
    imprints_two_dates = Record({
        'imprints': [
            {'date': '1998-04-30'},
            {'date': '2015-12-04'}
        ]
    })

    expected = '2015'
    result = Bibtex(imprints_two_dates)._get_year()

    assert expected == result


def test_get_year_from_preprint_date_an_empty_list():
    preprint_date_an_empty_list = Record({
        'preprint_date': []
    })

    expected = ''
    result = Bibtex(preprint_date_an_empty_list)._get_year()

    assert expected == result


def test_get_year_from_preprint_date_one_date():
    preprint_date_one_date = Record({
        'preprint_date': [
            '2015-12-04'
        ]
    })

    expected = '2015'
    result = Bibtex(preprint_date_one_date)._get_year()

    assert expected == result


def test_get_year_from_preprint_date_two_dates():
    preprint_date_two_dates = Record({
        'preprint_date': [
            '1998-04-30',
            '2015-12-04'
        ]
    })

    expected = '1998'
    result = Bibtex(preprint_date_two_dates)._get_year()

    assert expected == result


def test_get_journal_no_publication_info():
    no_publication_info = Record({})

    expected = ''
    result = Bibtex(no_publication_info)._get_journal()

    assert expected == result


def test_get_journal_publication_info_a_list_no_journal_title():
    publication_info_a_list_no_journal_title = Record({
        'publication_info': []
    })

    expected = ''
    result = Bibtex(publication_info_a_list_no_journal_title)._get_journal()

    assert expected == result


def test_get_journal_publication_info_a_list_one_journal_title():
    publication_info_a_list_one_journal_title = Record({
        'publication_info': [
            {'journal_title': 'Nucl.Phys.'}
        ]
    })

    expected = 'Nucl. Phys.'
    result = Bibtex(publication_info_a_list_one_journal_title)._get_journal()

    assert expected == result


def test_get_journal_publication_info_a_list_one_journal_title_a_list():
    publication_info_a_list_one_journal_title_a_list = Record({
        'publication_info': [
            {
                'journal_title': [
                    'Acta Phys.Polon.',
                    'Nucl.Phys.'
                ]
            }
        ]
    })

    expected = 'Nucl.Phys.'
    result = Bibtex(publication_info_a_list_one_journal_title_a_list)._get_journal()

    assert expected == result


def test_get_volume_no_publication_info_no_book_series():
    no_publication_info_no_book_series = Record({})

    expected = ''
    result = Bibtex(no_publication_info_no_book_series)._get_volume()

    assert expected == result


def test_get_volume_from_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    expected = ''
    result = Bibtex(publication_info_an_empty_list)._get_volume()

    assert expected == result


def test_get_volume_from_publication_info_a_list_one_with_volume():
    publication_info_a_list_one_with_volume = Record({
        'publication_info': [
            {'journal_volume': 'D89'}
        ]
    })

    expected = 'D89'
    result = Bibtex(publication_info_a_list_one_with_volume)._get_volume()

    assert expected == result


def test_get_volume_from_publication_info_one_with_volume_JHEP():
    publication_info_a_list_one_with_volume_JHEP = Record({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'journal_volume': '1511'
            }
        ]
    })

    expected = '11'
    result = Bibtex(publication_info_a_list_one_with_volume_JHEP)._get_volume()

    assert expected == result


def test_get_volume_from_publication_info_a_list_two_with_volume():
    publication_info_a_list_two_with_volume = Record({
        'publication_info': [
            {'journal_volume': 'D89'},
            {'journal_volume': 'D91'}
        ]
    })

    expected = 'D89'
    result = Bibtex(publication_info_a_list_two_with_volume)._get_volume()

    assert expected == result


def test_get_volume_from_publication_info_actually_from_book_series():
    publication_info_actually_from_book_series = Record({
        'publication_info': [],
        'book_series': [
            {'volume': '11'}
        ]
    })

    expected = '11'
    result = Bibtex(publication_info_actually_from_book_series)._get_volume()

    assert expected == result


def test_get_volume_from_book_series_an_empty_list():
    book_series_an_empty_list = Record({
        'book_series': []
    })

    expected = ''
    result = Bibtex(book_series_an_empty_list)._get_volume()

    assert expected == result


def test_get_volume_from_book_series_one_volume():
    book_series_one_volume = Record({
        'book_series': [
            {'volume': '11'}
        ]
    })

    expected = '11'
    result = Bibtex(book_series_one_volume)._get_volume()

    assert expected == result


def test_get_volume_from_book_series_two_volumes():
    book_series_two_volumes = Record({
        'book_series': [
            {'volume': '11'},
            {'volume': '5'}
        ]
    })

    expected = '5'
    result = Bibtex(book_series_two_volumes)._get_volume()

    assert expected == result


def test_get_number_no_publication_info():
    no_publication_info = Record({})

    expected = ''
    result = Bibtex(no_publication_info)._get_number()

    assert expected == result


def test_get_number_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    expected = ''
    result = Bibtex(publication_info_an_empty_list)._get_number()

    assert expected == result


def test_get_number_publication_info_a_list_one_issue():
    publication_info_a_list_one_issue = Record({
        'publication_info': [
            {'journal_issue': '5'}
        ]
    })

    expected = '5'
    result = Bibtex(publication_info_a_list_one_issue)._get_number()

    assert expected == result


def test_get_number_publication_info_a_list_two_issues():
    publication_info_a_list_two_issues = Record({
        'publication_info': [
            {'journal_issue': '11'},
            {'journal_issue': '5'}
        ]
    })

    expected = '11'
    result = Bibtex(publication_info_a_list_two_issues)._get_number()

    assert expected == result


def test_get_pages_no_publication_info():
    no_publication_info = Record({})

    expected = ''
    result = Bibtex(no_publication_info)._get_pages()

    assert expected == result


def test_get_pages_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    expected = ''
    result = Bibtex(publication_info_an_empty_list)._get_pages()

    assert expected == result


def test_get_pages_publication_info_one_page():
    publication_info_one_page = Record({
        'publication_info': [
            {'page_start': '585',
             'page_end': '587'}
        ]
    })

    expected = '585-587'
    result = Bibtex(publication_info_one_page)._get_pages()

    assert expected == result


def test_get_pages_publication_info_two_pages():
    publication_info_two_pages = Record({
        'publication_info': [
            {'page_start': '585',
             'page_end': '587'},
            {'page_start': '508',
             'page_end': '509'}
        ]
    })

    expected = '585-587'
    result = Bibtex(publication_info_two_pages)._get_pages()

    assert expected == result


def test_get_note_not_article_not_in_proceedings():
    record = Record({})

    not_article_not_in_proceedings = Bibtex(record)
    not_article_not_in_proceedings.entry_type = 'not-article'

    assert not_article_not_in_proceedings._get_note() is None


def test_get_note_no_publication_info():
    no_publication_info = Record({})

    assert Bibtex(no_publication_info)._get_note() is None


def test_get_note_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    expected = ''
    result = Bibtex(publication_info_an_empty_list)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_one_el():
    publication_info_a_list_one_el = Record({
        'publication_info': [
            {
                'note': 'Erratum',
                'journal_title': 'Phys.Rev.'
            }
        ]
    })

    expected = ''
    result = Bibtex(publication_info_a_list_one_el)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_two_els():
    publication_info_a_list_two_els = Record({
        'publication_info': [
            {
                'note': 'Erratum',
                'journal_title': 'Phys.Rev.'
            },
            {
                'note': 'Erratum',
                'journal_title': 'Phys.Rev.'
            }
        ]
    })

    expected = '[Erratum: Phys. Rev.]'
    result = Bibtex(publication_info_a_list_two_els)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_title():
    publication_info_a_list_not_a_note_with_title = Record({
        'publication_info': [
            {'journal_title': 'Phys.Rev.'},
            {'journal_title': 'Phys.Rev.'}
        ]
    })

    expected = '[Submitted to: Phys. Rev.]'
    result = Bibtex(publication_info_a_list_not_a_note_with_title)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_volume():
    publication_info_a_list_not_a_note_with_volume = Record({
        'publication_info': [
            {'journal_volume': 'D69'},
            {'journal_volume': 'D69'}
        ]
    })

    expected = '[]'
    result = Bibtex(publication_info_a_list_not_a_note_with_volume)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_volume_JHEP():
    publication_info_a_list_not_a_note_with_volume_JHEP = Record({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'journal_volume': '9712'
            },
            {
                'journal_title': 'JHEP',
                'journal_volume': '9712'
            }
        ]
    })

    expected = '[Submitted to: JHEP]'
    result = Bibtex(publication_info_a_list_not_a_note_with_volume_JHEP)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_issue():
    publication_info_a_list_not_a_note_with_issue = Record({
        'publication_info': [
            {'journal_issue': '11'},
            {'journal_issue': '11'}
        ]
    })

    expected = '[]'
    result = Bibtex(publication_info_a_list_not_a_note_with_issue)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_pages():
    publication_info_a_list_not_a_note_with_pages = Record({
        'publication_info': [
            {'page_start': 'pp.2067',
             'page_end': '2414'},
            {'page_start': 'pp.2067',
             'page_end': '2414'}
        ]
    })

    expected = '[]'
    result = Bibtex(publication_info_a_list_not_a_note_with_pages)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_year():
    publication_info_a_list_not_a_note_with_year = Record({
        'publication_info': [
            {'year': '2015'},
            {'year': '2015'}
        ]
    })

    expected = '[(2015)]'
    result = Bibtex(publication_info_a_list_not_a_note_with_year)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_preprint():
    publication_info_a_list_not_a_note_with_preprint = Record({
        'preprint_date': '2015-12-04',
        'publication_info': [
            {'journal_title': 'Acta Phys.Polon.'},
            {'journal_title': 'Acta Phys.Polon.'}
        ]
    })

    expected = '[Submitted to: Acta Phys. Polon.(2015)]'
    result = Bibtex(publication_info_a_list_not_a_note_with_preprint)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_not_a_note_with_everything():
    publication_info_a_list_not_a_note_with_everything = Record({
        'doi': 'something',
        'publication_info': [
            {
                'journal_title': 'Acta Phys.Polon.',
                'journal_volume': 'B46',
                'journal_issue': '11',
                'page_start': 'pp.2067',
                'page_end': '2414'
            },
            {
                'journal_title': 'Acta Phys.Polon.',
                'journal_volume': 'B46',
                'journal_issue': '11',
                'page_start': 'pp.2067',
                'page_end': '2414'
            },
        ]
    })

    expected = '[Acta Phys. Polon.B46,no.11,pp.2067]'
    result = Bibtex(publication_info_a_list_not_a_note_with_everything)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_a_note_with_title():
    publication_info_a_list_a_note_with_title = Record({
        'publication_info': [
            {
                'note': 'Erratum',
                'journal_title': 'Phys.Rev.'
            },
            {
                'note': 'Erratum',
                'journal_title': 'Phys.Rev.'
            }
        ]
    })

    expected = '[Erratum: Phys. Rev.]'
    result = Bibtex(publication_info_a_list_a_note_with_title)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_a_note_with_volume():
    publication_info_a_list_a_note_with_volume = Record({
        'publication_info': [
            {
                'note': 'Addendum',
                'journal_volume': 'D91'
            },
            {
                'note': 'Addendum',
                'journal_volume': 'D91'
            }
        ]
    })

    expected = '[Addendum: D91]'
    result = Bibtex(publication_info_a_list_a_note_with_volume)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_a_note_with_volume_JHEP():
    publication_info_a_list_a_note_with_volume_JHEP = Record({
        'publication_info': [
            {
                'note': 'Erratum',
                'journal_title': 'JHEP',
                'journal_volume': '1501'
            },
            {
                'note': 'Erratum',
                'journal_title': 'JHEP',
                'journal_volume': '1501'
            }
        ]
    })

    expected = '[Erratum: JHEP01]'
    result = Bibtex(publication_info_a_list_a_note_with_volume_JHEP)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_a_note_with_issue():
    publication_info_a_list_a_note_with_issue = Record({
        'publication_info': [
            {
                'note': 'Corrigendum',
                'journal_issue': '1'
            },
            {
                'note': 'Corrigendum',
                'journal_issue': '1'
            }
        ]
    })

    expected = '[Corrigendum: ,no.1]'
    result = Bibtex(publication_info_a_list_a_note_with_issue)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_a_note_with_pages():
    publication_info_a_list_a_note_with_pages = Record({
        'publication_info': [
            {
                'note': 'Reprint',
                'artid': '019903'
            },
            {
                'note': 'Reprint',
                'artid': '019903'
            }
        ]
    })

    expected = '[Reprint: ,019903]'
    result = Bibtex(publication_info_a_list_a_note_with_pages)._get_note()

    assert expected == result


def test_get_note_publication_info_a_list_a_note_with_year():
    publication_info_a_list_a_note_with_year = Record({
        'publication_info': [
            {
                'note': 'Erratum',
                'year': '2015'
            },
            {
                'note': 'Erratum',
                'year': '2015'
            }
        ]
    })

    expected = '[Erratum: (2015)]'
    result = Bibtex(publication_info_a_list_a_note_with_year)._get_note()

    assert expected == result


def test_get_url_no_urls():
    no_urls = Record({})

    expected = ''
    result = Bibtex(no_urls)._get_url()

    assert expected == result


def test_get_url_empty_urls():
    empty_urls = Record({
        'urls': []
    })

    expected = ''
    result = Bibtex(empty_urls)._get_url()

    assert expected == result


def test_get_url_urls_without_value():
    urls_without_url = Record({
        'urls': [
            {'not-value': 'foo'}
        ]
    })

    expected = ''
    result = Bibtex(urls_without_url)._get_url()

    assert expected == result


def test_get_url_one_url_to_an_image():
    one_url_to_an_image = Record({
        'urls': [
            {'value': 'foo.jpg'}
        ]
    })

    expected = ''
    result = Bibtex(one_url_to_an_image)._get_url()

    assert expected == result


def test_get_url_one_url_not_to_an_image():
    one_url_not_to_an_image = Record({
        'urls': [
            {'value': 'http://link.aps.org/abstract/PRL/V19/P1264'}
        ]
    })

    expected = 'http://link.aps.org/abstract/PRL/V19/P1264'
    result = Bibtex(one_url_not_to_an_image)._get_url()

    assert expected == result


def test_get_url_more_urls_selects_first():
    more_urls = Record({
        'urls': [
            {'value': 'http://link.aps.org/abstract/PRL/V19/P1264'},
            {'value': 'http://example.com'}
        ]
    })

    expected = 'http://link.aps.org/abstract/PRL/V19/P1264'
    result = Bibtex(more_urls)._get_url()

    assert expected == result


def test_get_eprint_no_arxiv_field():
    no_arxiv_field = Record({})

    expected = []
    result = Bibtex(no_arxiv_field)._get_eprint()

    assert expected == result


def test_get_eprint_arxiv_field_starts_with_arxiv():
    starts_with_arxiv = Record({
        'arxiv_eprints': [
            {'value': 'arXiv:1512.01381'}
        ]
    })

    expected = '1512.01381'
    result = Bibtex(starts_with_arxiv)._get_eprint()

    assert expected == result


def test_get_eprint_arxiv_field_does_not_start_with_arxiv():
    does_not_start_with_arxiv = Record({
        'arxiv_eprints': [
            {'value': '1512.01381'}
        ]
    })

    expected = '1512.01381'
    result = Bibtex(does_not_start_with_arxiv)._get_eprint()

    assert expected == result


def test_get_archive_prefix_no_arxiv_eprints():
    no_arxiv_eprints = Record({})

    expected = ''
    result = Bibtex(no_arxiv_eprints)._get_archive_prefix()

    assert expected == result


def test_get_archive_prefix_empty_arxiv_eprints():
    empty_arxiv_eprints = Record({
        'arxiv_eprints': []
    })

    expected = ''
    result = Bibtex(empty_arxiv_eprints)._get_archive_prefix()

    assert expected == result


def test_get_archive_prefix_some_arxiv_eprints():
    some_arxiv_eprints = Record({
        'arxiv_eprints': [
            {
                u'categories': [u'hep-th'],
                u'value': u'hep-th/9709220'
            }
        ]
    })

    expected = 'arXiv'
    result = Bibtex(some_arxiv_eprints)._get_archive_prefix()

    assert expected == result


def test_get_primary_class_no_arxiv_eprints():
    no_arxiv_eprints = Record({})

    expected = ''
    result = Bibtex(no_arxiv_eprints)._get_primary_class()

    assert expected == result


def test_get_primary_class_empty_arxiv_eprints():
    empty_arxiv_eprints = Record({
        'arxiv_eprints': []
    })

    assert Bibtex(empty_arxiv_eprints)._get_primary_class() is None


def test_get_primary_class_one_arxiv_eprint_one_category():
    one_arxiv_eprint_one_category = Record({
        'arxiv_eprints': [
            {'categories': ['hep-th']}
        ]
    })

    expected = 'hep-th'
    result = Bibtex(one_arxiv_eprint_one_category)._get_primary_class()

    assert expected == result


def test_get_primary_class_one_arxiv_eprint_more_categories():
    one_arxiv_eprint_more_categories = Record({
        'arxiv_eprints': [
            {'categories': ['hep-th', 'hep-ph']}
        ]
    })

    expected = 'hep-th'
    result = Bibtex(one_arxiv_eprint_more_categories)._get_primary_class()

    assert expected == result


def test_get_primary_class_more_arxiv_eprints_more_categories():
    more_arxiv_eprints_more_categories = Record({
        'arxiv_eprints': [
            {'categories': ['hep-th', 'hep-ph']},
            {'categories': ['hep-ex']}
        ]
    })

    expected = 'hep-th'
    result = Bibtex(more_arxiv_eprints_more_categories)._get_primary_class()

    assert expected == result


def test_get_series_no_book_series():
    no_book_series = Record({})

    expected = ''
    result = Bibtex(no_book_series)._get_series()

    assert expected == result


def test_get_series_empty_book_series():
    empty_book_series = Record({
        'book_series': []
    })

    expected = ''
    result = Bibtex(empty_book_series)._get_series()

    assert expected == result


def test_get_series_one_book_series():
    one_book_series = Record({
        'book_series': [
            {'value': 'Mathematical Physics Studies'}
        ]
    })

    expected = 'Mathematical Physics Studies'
    result = Bibtex(one_book_series)._get_series()

    assert expected == result


def test_get_series_more_book_series():
    more_book_series = Record({
        'book_series': [
            {'value': 'High Energy Physics'},
            {'value': 'Mathematical Physics Studies'}
        ]
    })

    expected = 'Mathematical Physics Studies'
    result = Bibtex(more_book_series)._get_series()

    assert expected == result


def test_get_isbn_no_isbns():
    no_isbns = Record({})

    expected = ''
    result = Bibtex(no_isbns)._get_isbn()

    assert expected == result


@pytest.mark.xfail
def test_get_isbn_empty_isbns():
    empty_isbns = Record({
        'isbns': []
    })

    Bibtex(empty_isbns)._get_isbn()


@pytest.mark.xfail
def test_get_isbn_one_isbn_not_a_list():
    one_isbn_not_a_list = Record({
        'isbns': [
            {'value': '978-1-4244-0922-8'}
        ]
    })

    expected = '978-1-4244-0922-8'
    result = Bibtex(one_isbn_not_a_list)._get_isbn()

    assert expected == result


def test_get_isbn_two_isbns_not_a_list():
    two_isbns_not_a_list = Record({
        'isbns': [
            {'value': '978-3-319-17544-7'},
            {'value': '978-3-319-17545-4'}
        ]
    })

    expected = '978-3-319-17544-7, 978-3-319-17545-4'
    result = Bibtex(two_isbns_not_a_list)._get_isbn()

    assert expected == result


def test_get_isbn_two_isbns_one_a_list():
    two_isbns_one_a_list = Record({
        'isbns': [
            {'value': ['978-3-319-17544-7', '978-3-319-17545-4']},
            {'value': '978-94-010-2276-7'}
        ]
    })

    expected = '978-3-319-17544-7, 978-94-010-2276-7'
    result = Bibtex(two_isbns_one_a_list)._get_isbn()

    assert expected == result


def test_get_pubnote_no_publication_info():
    no_publication_info = Record({})

    expected = ''
    result = Bibtex(no_publication_info)._get_pubnote()

    assert expected == result


def test_get_pubnote_publication_info_an_empty_list():
    publication_info_an_empty_list = Record({
        'publication_info': []
    })

    assert Bibtex(publication_info_an_empty_list)._get_pubnote() is None


def test_get_pubnote_publication_info_a_list_one_with_title():
    publication_info_a_list_one_with_title = Record({
        'publication_info': [
            {'journal_title': 'Nucl.Phys.'}
        ]
    })

    assert Bibtex(publication_info_a_list_one_with_title)._get_pubnote() is None


@pytest.mark.xfail
@mock.patch('inspirehep.utils.bibtex.get_kbr_keys')
def test_get_pubnote_publication_info_a_list_one_with_title_and_volume(self, g_k_k):
    # TODO: mock the actual invenio_knowledge API.
    g_k_k.return_value = [['Nucl. Phys.']]

    publication_info_a_list_one_with_title_and_volume = Record({
        'publication_info': [
            {
                'journal_title': 'Nucl.Phys.',
                'journal_volume': '22'
            }
        ]
    })

    expected = 'Nucl. Phys.,22,'
    result = Bibtex(publication_info_a_list_one_with_title_and_volume)._get_pubnote()

    assert expected == result


@pytest.mark.xfail
@mock.patch('inspirehep.utils.bibtex.get_kbr_keys')
def test_get_pubnote_publication_info_a_list_one_with_title_and_pages_not_a_list(self, g_k_k):
    # TODO: mock the actual invenio_knowledge API.
    g_k_k.return_value = [['Nucl. Phys.']]

    publication_info_a_list_one_with_title_and_pages_not_a_list = Record({
        'publication_info': [
            {
                'journal_title': 'Nucl.Phys.',
                'page_start': '579',
                'page_end': '588'
            }
        ]
    })

    expected = 'Nucl. Phys.,,579'
    result = Bibtex(publication_info_a_list_one_with_title_and_pages_not_a_list)._get_pubnote()

    assert expected == result


@pytest.mark.xfail
@mock.patch('inspirehep.utils.bibtex.get_kbr_keys')
def test_get_pubnote_publication_info_a_list_one_with_everything(self, g_k_k):
    # TODO: mock the actual invenio_knowledge API.
    g_k_k.return_value = [['Nucl. Phys.']]

    publication_info_a_list_one_with_everything = Record({
        'publication_info': [
            {
                'journal_title': 'Nucl.Phys.',
                'journal_volume': '22',
                'page_start': '579',
                'page_end': '588'
            }
        ]
    })

    expected = 'Nucl. Phys.,22,579'
    result = Bibtex(publication_info_a_list_one_with_everything)._get_pubnote()

    assert expected == result


@pytest.mark.xfail
@mock.patch('inspirehep.utils.bibtex.get_kbr_keys')
def test_get_pubnote_publication_info_a_list_get_kbr_keys_raises(self, g_k_k):
    # TODO: mock the actual invenio_knowledge API.
    g_k_k.side_effect = RuntimeError

    publication_info_a_list_one_with_everything = Record({
        'publication_info': [
            {
                'journal_title': 'Nucl.Phys.',
                'journal_volume': '22',
                'page_start': '579',
                'page_end': '588'
            }
        ]
    })

    expected = ''
    result = Bibtex(publication_info_a_list_one_with_everything)._get_pubnote()

    assert expected == result
