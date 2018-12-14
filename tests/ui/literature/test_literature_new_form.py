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

import pytest

from inspirehep.bat.pages import (
    literature_submission_form,
    holdingpen_literature_detail,
    holdingpen_literature_list,
)


def _accept_and_complete(input_data):
    holdingpen_literature_list.go_to()
    holdingpen_literature_list.assert_first_record_matches(input_data)

    holdingpen_literature_detail.go_to()
    holdingpen_literature_detail.assert_first_record_matches(input_data)
    holdingpen_literature_detail.accept_record().assert_has_no_errors()

    holdingpen_literature_list.go_to()
    holdingpen_literature_list.assert_first_record_matches(input_data)
    holdingpen_literature_list.assert_first_record_completed()


def test_literature_create_chapter(login):
    input_data = literature_submission_form.InputData()
    input_data.add_basic_info(
        abstract='Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        title='My Title For Test',
        language='ru',
        title_translation='My Title was in Russian',
        collaboration='This is a collaboration',
        experiment='This is an experiment',
        authors=(
            {'name': 'Barry White', 'affiliation': 'Wisconsin U., Madison'},
            {'name': 'James Brown', 'affiliation': 'CERN'},
        ),
        report_numbers=('100', '101'),
        subjects=('Accelerators', 'Computing'),
    )
    input_data.add_links(pdf_url='http://example.com/a-pdf')
    input_data.add_references_comments(
        references='references',
        extra_comments='comments about the document',
    )
    input_data.add_book_chapter_info(
        book_title='Relativistic Quantum Mechanics',
        page_start='512',
        page_end='1024',
    )

    literature_submission_form.go_to()

    literature_submission_form.submit_chapter(input_data).assert_has_no_errors()
    _accept_and_complete(input_data)


def test_literature_create_book(login):
    input_data = literature_submission_form.InputData()
    input_data.add_basic_info(
        abstract='Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        title='My Title For Test',
        language='ru',
        title_translation='My Title was in Russian',
        collaboration='This is a collaboration',
        experiment='This is an experiment',
        authors=(
            {'name': 'Barry White', 'affiliation': 'Wisconsin U., Madison'},
            {'name': 'James Brown', 'affiliation': 'CERN'},
        ),
        report_numbers=('100', '101'),
        subjects=('Accelerators', 'Computing'),
    )
    input_data.add_links(pdf_url='http://example.com/a-pdf')
    input_data.add_references_comments(
        references='references',
        extra_comments='comments about the document',
    )
    input_data.add_book_info(
        book_title='Astrowars',
        book_volume='Andromeda',
        publication_date='2001-01-01',
        publication_place='Oxford',
        publisher_name='Oxford University',
    )

    literature_submission_form.go_to()

    literature_submission_form.submit_book(input_data).assert_has_no_errors()
    _accept_and_complete(input_data)


def test_literature_create_thesis(login):
    input_data = literature_submission_form.InputData()
    input_data.add_basic_info(
        abstract='Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        title='My Title For Test',
        language='ru',
        title_translation='My Title was in Russian',
        collaboration='This is a collaboration',
        experiment='This is an experiment',
        authors=(
            {'name': 'Barry White', 'affiliation': 'Wisconsin U., Madison'},
            {'name': 'James Brown', 'affiliation': 'CERN'},
        ),
        report_numbers=('100', '101'),
        subjects=('Accelerators', 'Computing'),
    )
    input_data.add_links(pdf_url='http://example.com/a-pdf')
    input_data.add_references_comments(
        references='references',
        extra_comments='comments about the document',
    )
    input_data.add_thesis_info(
        supervisor_name='Mister Yellow',
        supervisor_affiliation='CERN',
        thesis_date='2001-01-01',
        defense_date='2002-02-01',
        degree_type='bachelor',
        institution='Wisconsin U., Madison',
    )

    literature_submission_form.go_to()
    literature_submission_form.submit_thesis(input_data).assert_has_no_errors()
    _accept_and_complete(input_data)


def test_literature_create_article_journal(login):
    input_data = literature_submission_form.InputData(
        {
        }
    )
    input_data.add_basic_info(
        abstract='Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        title='My Title For Test',
        language='ru',
        title_translation='My Title was in Russian',
        collaboration='This is a collaboration',
        experiment='This is an experiment',
        authors=(
            {'name': 'Barry White', 'affiliation': 'Wisconsin U., Madison'},
            {'name': 'James Brown', 'affiliation': 'CERN'},
        ),
        report_numbers=('100', '101'),
        subjects=('Accelerators', 'Computing'),
    )
    input_data.add_links(pdf_url='http://example.com/a-pdf')
    input_data.add_references_comments(
        references='references',
        extra_comments='comments about the document',
    )
    input_data.add_journal_info(
        journal_title='europe',
        volume='Volume',
        issue='issue',
        year='2014',
        page_range='100-110',
        conf_name='This Conference',
    )

    literature_submission_form.go_to()

    literature_submission_form.submit_journal_article(
        input_data
    ).assert_has_no_errors()
    _accept_and_complete(input_data)


def test_literature_create_article_journal_with_proceeding(login):
    input_data = literature_submission_form.InputData()
    input_data.add_basic_info(
        abstract='Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
        title='My Title For Test',
        language='ru',
        title_translation='My Title was in Russian',
        collaboration='This is a collaboration',
        experiment='This is an experiment',
        authors=(
            {'name': 'Barry White', 'affiliation': 'Wisconsin U., Madison'},
            {'name': 'James Brown', 'affiliation': 'CERN'},
        ),
        report_numbers=('100', '101'),
        subjects=('Accelerators', 'Computing'),
    )
    input_data.add_links(pdf_url='http://example.com/a-pdf')
    input_data.add_references_comments(
        references='references',
        extra_comments='comments about the document',
    )
    input_data.add_journal_info(
        journal_title='europe',
        volume='Volume',
        issue='issue',
        year='2014',
        page_range='100-110',
        conf_name='This Conference',
    )
    input_data.add_proceedings(nonpublic_note='This proceedings')

    literature_submission_form.go_to()

    literature_submission_form.submit_journal_article_with_proceeding(
        input_data
    ).assert_has_no_errors()
    _accept_and_complete(input_data)


def test_thesis_info_autocomplete_supervisor_institution(login):
    literature_submission_form.go_to()
    literature_submission_form.write_institution_thesis(
        'CER',
        'CERN',
    ).assert_has_no_errors()


def test_journal_info_autocomplete_title(login):
    literature_submission_form.go_to()
    literature_submission_form.write_journal_title(
        'Nuc',
        'Nucl.Phys.',
    ).assert_has_no_errors()


@pytest.mark.xfail
def test_conference_info_autocomplete_title(login):
    literature_submission_form.go_to()
    literature_submission_form.write_conference(
        'autrans',
        'IN2P3 School of Statistics, 2012-05-28, Autrans, FR',
    ).assert_has_no_errors()


def test_basic_info_autocomplete_affiliation(login):
    literature_submission_form.go_to()
    literature_submission_form.write_affiliation(
        'oxf',
        'Oxford U.',
    ).assert_has_no_errors()


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

    literature_submission_form.go_to()
    literature_submission_form.submit_arxiv_id(
        'hep-th/9711200',
        expected_data,
    ).assert_has_no_errors()


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

    literature_submission_form.go_to()

    literature_submission_form.submit_doi_id(
        '10.1086/305772',
        expected_data,
    ).assert_has_no_errors()
