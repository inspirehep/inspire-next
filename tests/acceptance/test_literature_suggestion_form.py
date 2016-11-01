# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
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

from __future__ import absolute_import, division, print_function

from bat_framework.pages import create_literature


# Components Tests
def test_thesis_info_date(login):
    """Test the format for the submission and defense date in the thesis section"""
    create_literature.go_to()
    _test_date_format('thesis_date', 'state-thesis_date')
    _test_date_format('thesis_date', 'state-thesis_date')


def test_thesis_info_autocomplete_supervisor_institution(login):
    """Test the autocompletion for the supervisor institution in the thesis section"""
    create_literature.go_to()
    assert 'CERN' in create_literature.write_institution_thesis('CER')


def test_journal_info_autocomplete_title(login):
    """Test the autocompletion for the title in the journal info section"""
    create_literature.go_to()
    assert 'Nuclear Physics' in create_literature.write_journal_title('Nuc')


def test_conference_info_autocomplete_title(login):
    """Test the autocompletion for the title in the conference info section"""
    create_literature.go_to()
    assert 'IN2P3 School of Statistics, 2012-05-28, Autrans, France' in create_literature.write_conference('sos')


def test_basic_info_autocomplete_affilation(login):
    """Test the autocompletion for the affilation in the basic info section"""
    create_literature.go_to()
    assert 'Oxford U.' in create_literature.write_affilation('oxf')


def test_import_from_arXiv(login):
    """Test the import from arXiv"""
    create_literature.go_to()
    imported_data = create_literature.submit_arxiv_id('hep-th/9711200')

    test_data = {
        'issue': '4',
        'year': '1999',
        'volume': '38',
        'page-range': '1113-1133',
        'author': 'Maldacena, Juan',
        'doi': '10.1023/A:1026654312961',
        'journal': 'International Journal of Theoretical Physics',
        'title': 'The Large N Limit of Superconformal Field Theories and Supergravity',
        'abstract': 'We show that the large $N$ limit of certain conformal field theories'
        }

    assert imported_data == test_data


def test_import_from_doi(login):
    create_literature.go_to()
    imported_data = create_literature.submit_doi_id('10.1086/305772')

    test_data = {
        'issue': '2',
        'year': '1998',
        'volume': '500',
        'page-range': '525-553',
        'author': 'Schlegel, David J.',
        'author-1': 'Finkbeiner, Douglas P.',
        'author-2': 'Davis, Marc',
        'journal': 'The Astrophysical Journal',
        'title': 'Maps of Dust Infrared Emission for Use in Estimation of Reddening and Cosmic Microwave Background Radiation Foregrounds'
        }

    assert imported_data == test_data


def test_format_input_arXiv(login):
    create_literature.go_to()
    assert 'The provided ArXiv ID is invalid - it should look' not in create_literature.write_arxiv_id('1001.4538')
    assert 'The provided ArXiv ID is invalid - it should look' in create_literature.write_arxiv_id('hep-th.9711200')
    assert 'The provided ArXiv ID is invalid - it should look' not in create_literature.write_arxiv_id('hep-th/9711200')


def test_format_input_doi(login):
    create_literature.go_to()
    assert 'The provided DOI is invalid - it should look' in create_literature.write_doi_id('dummy:10.1086/305772')
    assert 'The provided DOI is invalid - it should look' not in create_literature.write_doi_id('10.1086/305772')
    assert 'The provided DOI is invalid - it should look' in create_literature.write_doi_id('state-doi')


def _test_date_format(field_id, field_err_id):
    message_error = 'Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM or YYYY.'
    assert message_error not in create_literature.write_date_thesis(field_id, field_err_id, '')
    assert message_error in create_literature.write_date_thesis(field_id, field_err_id, 'wrong')
    assert message_error not in create_literature.write_date_thesis(field_id, field_err_id, '2016-01')
    assert message_error in create_literature.write_date_thesis(field_id, field_err_id, '2016-02-30')
    assert message_error not in create_literature.write_date_thesis(field_id, field_err_id, '2016')
    assert message_error in create_literature.write_date_thesis(field_id, field_err_id, '2016-13')
