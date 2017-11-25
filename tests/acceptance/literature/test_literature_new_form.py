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

from inspirehep.bat.pages import (
    create_literature,
    holding_panel_literature_detail,
    holding_panel_literature_list,
)


def test_literature_create_chapter_manually(login):
    input_data = {
        'pdf-1': 'http://example.com/a-pdf',
        'title': 'My Title For Test',
        'language': 'ru',
        'title_translation': 'My Title was in Russian',
        'subject': 'Computing',
        'author-0': 'Barry White',
        'author-0-affiliation': 'Wisconsin U., Madison',
        'author-1': 'James Brown',
        'author-1-affiliation': 'CERN',
        'collaboration': 'This is a collaboration',
        'experiment': 'This is an experiment',
        'abstract': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        'report-number-0': '100',
        'report-number-1': '101',
        'book-title': 'Relativistic Quantum Mechanics',
        'page-start': '512',
        'page-end': '1024',
        'references': 'references',
        'extra-comments': 'comments about the document'
    }

    create_literature.go_to()
    assert create_literature.submit_chapter(input_data).has_error()
    _check_back_office(input_data)


def test_literature_create_book_manually(login):
    input_data = {
        'pdf-1': 'http://example.com/a-pdf',
        'title': 'My Title For Test',
        'language': 'ru',
        'title_translation': 'My Title was in Russian',
        'subject': 'Computing',
        'author-0': 'Barry White',
        'author-0-affiliation': 'Wisconsin U., Madison',
        'author-1': 'James Brown',
        'author-1-affiliation': 'CERN',
        'collaboration': 'This is a collaboration',
        'experiment': 'This is an experiment',
        'abstract': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        'report-number-0': '100',
        'report-number-1': '101',
        'publisher-name': 'Oxford University',
        'publication-date': '2001-01-01',
        'publication-place': 'Oxford',
        'book-edition': 'No 2',
        'book-title': 'Astrowars',
        'book-volume': 'Andromeda',
        'references': 'references',
        'extra-comments': 'comments about the document'
    }

    create_literature.go_to()
    assert create_literature.submit_book(input_data).has_error()
    _check_back_office(input_data)


def test_literature_create_thesis_manually(login):
    input_data = {
        'pdf-1': 'http://example.com/a-pdf',
        'title': 'My Title For Test',
        'language': 'ru',
        'title_translation': 'My Title was in Russian',
        'subject': 'Computing',
        'author-0': 'Barry White',
        'author-0-affiliation': 'Wisconsin U., Madison',
        'author-1': 'James Brown',
        'author-1-affiliation': 'CERN',
        'collaboration': 'This is a collaboration',
        'experiment': 'This is an experiment',
        'abstract': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        'report-number-0': '100',
        'report-number-1': '101',
        'supervisor': 'Mister Yellow',
        'supervisor-affiliation': 'CERN',
        'thesis-date': '2001-01-01',
        'defense-date': '2002-02-01',
        'degree-type': 'bachelor',
        'institution': 'Wisconsin U., Madison',
        'references': 'references',
        'extra-comments': 'comments about the document'
    }

    create_literature.go_to()
    assert create_literature.submit_thesis(input_data).has_error()
    _check_back_office(input_data)


def test_literature_create_article_journal_manually(login):
    input_data = {
        'pdf-1': 'http://example.com/a-pdf',
        'title': 'My Title For Test',
        'language': 'ru',
        'title_translation': 'My Title was in Russian',
        'subject': 'Computing',
        'author-0': 'Barry White',
        'author-0-affiliation': 'Wisconsin U., Madison',
        'author-1': 'James Brown',
        'author-1-affiliation': 'CERN',
        'collaboration': 'This is a collaboration',
        'experiment': 'This is an experiment',
        'abstract': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        'report-number-0': '100',
        'report-number-1': '101',
        'journal_title': 'europe',
        'volume': 'Volume',
        'issue': 'issue',
        'year': '2014',
        'page-range-article': '100-110',
        'conf-name': 'This Conference',
        'references': 'references',
        'extra-comments': 'comments about the document'
    }

    create_literature.go_to()
    assert create_literature.submit_journal_article(input_data).has_error()
    _check_back_office(input_data)


def test_literature_create_article_journal_with_proceeding_manually(login):
    input_data = {
        'pdf-1': 'http://example.com/a-pdf',
        'title': 'My Title For Test',
        'language': 'ru',
        'title_translation': 'My Title was in Russian',
        'subject': 'Computing',
        'author-0': 'Barry White',
        'author-0-affiliation': 'Wisconsin U., Madison',
        'author-1': 'James Brown',
        'author-1-affiliation': 'CERN',
        'collaboration': 'This is a collaboration',
        'experiment': 'This is a experiment',
        'abstract': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        'report-number-0': '100',
        'report-number-1': '101',
        'journal_title': 'europe',
        'volume': 'Volume',
        'issue': 'issue',
        'year': '2014',
        'page-range-article': '100-110',
        'conf-name': 'This Conference',
        'non-public-note': 'This proceedings',
        'references': 'references',
        'extra-comments': 'comments about the document'
    }

    create_literature.go_to()
    assert create_literature.submit_journal_article_with_proceeding(
        input_data
    ).has_error()
    _check_back_office(input_data)


def _check_back_office(input_data):
    holding_panel_literature_list.go_to()
    assert holding_panel_literature_list.load_submitted_record().has_error()

    holding_panel_literature_detail.go_to()
    assert holding_panel_literature_detail.load_submitted_record(
        input_data
    ).has_error()
    assert holding_panel_literature_detail.accept_record().has_error()

    holding_panel_literature_list.go_to()
    assert holding_panel_literature_list.load_completed_record().has_error()


def test_thesis_info_autocomplete_supervisor_institution(login):
    create_literature.go_to()
    assert create_literature.write_institution_thesis(
        'CER',
        'CERN',
    ).has_error()


def test_journal_info_autocomplete_title(login):
    create_literature.go_to()
    assert create_literature.write_journal_title(
        'Nuc',
        'Nucl.Phys.',
    ).has_error()


def test_conference_info_autocomplete_title(login):
    create_literature.go_to()
    assert create_literature.write_conference(
        'autrans',
        'IN2P3 School of Statistics, 2012-05-28, Autrans, FR',
    ).has_error()


def test_basic_info_autocomplete_affiliation(login):
    create_literature.go_to()
    assert create_literature.write_affiliation('oxf', 'Oxford U.').has_error()


def test_import_from_arXiv(login):
    expected_data = {
        'issue': '4',
        'year': '1999',
        'volume': '38',
        'page-range': '1113-1133',
        'author': 'Maldacena, Juan',
        'doi': '10.1023/A:1026654312961',
        'journal': 'International Journal of Theoretical Physics',
        'title': (
            'The Large N Limit of Superconformal Field Theories and '
            'Supergravity'
        ),
        'abstract': (
            'We show that the large $N$ limit of certain conformal field '
            'theories'
        ),
    }

    create_literature.go_to()
    assert create_literature.submit_arxiv_id(
        'hep-th/9711200',
        expected_data,
    ).has_error()


def test_import_from_doi(login):
    expected_data = {
        'issue': '2',
        'year': '1998',
        'volume': '500',
        'page-range': '525-553',
        'author': 'Schlegel, David J.',
        'author-1': 'Finkbeiner, Douglas P.',
        'author-2': 'Davis, Marc',
        'journal': 'The Astrophysical Journal',
        'title': (
            'Maps of Dust Infrared Emission for Use in Estimation of '
            'Reddening and Cosmic Microwave Background Radiation Foregrounds'
        ),
    }

    create_literature.go_to()
    assert create_literature.submit_doi_id(
        '10.1086/305772',
        expected_data,
    ).has_error()
