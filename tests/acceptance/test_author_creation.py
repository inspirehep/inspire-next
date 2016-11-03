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

from bat_framework.pages import create_author
from bat_framework.pages import holding_panel_author_list
from bat_framework.pages import holding_panel_author_detail

input_author_data = {
    'given-names': 'Mark',
    'family-name': 'Twain',
    'display-name': 'M. Twain',
    'native-name': 'M. Twain',
    'public-email': 'mark.twain@history.org',
    'orcid': '1111-1111-1111-1111',
    'websites-0': 'http://www.example1.com',
    'websites-1': 'http://www.example2.com',
    'linkedin-url': 'http://www.example3.com',
    'twitter-url': 'http://www.example4.com',
    'blog-url': 'http://www.example5.com',
    'institution-name': 'CERN',
    'institution-start_year': '2000',
    'institution-end_year': '2001',
    'institution-rank': 'STAFF',
    'experiments-name': 'ATLAS',
    'experiments-start_year': '2002',
    'experiments-end_year': '2005',
    'advisors-name': 'Bob White',
    'advisors-degree_type': 'PhD',
    'comments': 'Some comments about the author',
    'subject-0': 'ACC-PHYS',
    'subject-1': 'ASTRO-PH'
}

def test_institutions_typehead(login):
    create_author.go_to()
    assert 'CERN' in create_author.write_institution('cer')


def test_experiments_typehead(login):
    create_author.go_to()
    assert 'ATLAS' in create_author.write_experiment('atl')


def test_advisors_typehead(login):
    create_author.go_to()
    assert 'Vorobyev, Alexey' in create_author.write_advisor('alexe')


def test_mail_format(login):
    """Test mail format in Personal Information for an author"""
    create_author.go_to()
    assert 'Invalid email address.' in create_author.write_mail('wrong.mail')
    assert 'Invalid email address.' not in create_author.write_mail('me@me.com')


def test_ORCID_format(login):
    """Test ORCID format in Personal Information for an author"""
    create_author.go_to()
    assert 'A valid ORCID iD consists of 16 digits separated by dashes.' in create_author.write_orcid('wrong.ORCID')
    assert 'A valid ORCID iD consists of 16 digits separated by dashes.' not in create_author.write_orcid('1111-1111-1111-1111')


def test_institutions_years(login):
    """Test format in Start Year and End Year for author institutions"""
    create_author.go_to()
    input_id = 'institution_history-0-start_year'
    error_mess_id = 'state-institution_history-0-start_year'
    assert 'is not a valid year' in create_author.write_year(input_id, error_mess_id, 'wrongyear')
    assert 'is not a valid year' not in create_author.write_year(input_id, error_mess_id, '2016')
    input_id = 'institution_history-0-end_year'
    error_mess_id = 'state-institution_history-0-end_year'
    assert 'is not a valid year' in create_author.write_year(input_id, error_mess_id, 'wrongyear')
    assert 'is not a valid year' not in create_author.write_year(input_id, error_mess_id, '2016')


def test_experiments_years(login):
    """Test format in Start Year and End Year for author experiments"""
    create_author.go_to()
    input_id = 'experiments-0-start_year'
    error_mess_id = 'state-experiments-0-start_year'
    assert 'is not a valid year' in create_author.write_year(input_id, error_mess_id, 'wrongyear')
    assert 'is not a valid year' not in create_author.write_year(input_id, error_mess_id, '2016')
    input_id = 'experiments-0-end_year'
    error_mess_id = 'state-experiments-0-end_year'
    assert 'is not a valid year' in create_author.write_year(input_id, error_mess_id, 'wrongyear')
    assert 'is not a valid year' not in create_author.write_year(input_id, error_mess_id, '2016')


def test_mandatory_fields(login):
    create_author.go_to()
    expected_data = {
            'given-name': 'This field is required.',
            'display-name': 'This field is required.',
            'reserach-field': 'This field is required.'
            }
    assert expected_data == create_author.submit_empty_form()


def test_submit_author(login):
    """Submit the form for author creation from scratch"""
    create_author.go_to()
    assert 'Thank you for adding new profile information!' in create_author.submit_author(input_author_data)

    holding_panel_author_list.go_to()
    record = holding_panel_author_list.load_submission_record(input_author_data)
    assert 'CERN' in record
    assert 'ACC-PHYS' in record
    assert 'ASTRO-PH' in record
    assert 'Twain, Mark' in record
    assert 'inspire:uid:1' in record
    assert 'admin@inspirehep.net' in record

    holding_panel_author_detail.go_to()
    record = holding_panel_author_detail.load_submitted_record(input_author_data)
    assert 'M. Twain' in record
    assert 'M. Twain' in record
    assert 'Twain, Mark' in record
    assert 'mark.twain@history.org' in record
    assert 'Experiment: ATLAS - From: 2002 To: 2005' in record
    assert 'Submitted by admin@inspirehep.net\non' in record
    assert 'Some comments about the author' in record
    assert 'http://www.example1.com' in record
    assert 'http://www.example2.com' in record
    assert 'http://www.example3.com' in record
    assert 'http://www.example4.com' in record
    assert 'http://www.example5.com' in record
    assert 'ACC-PHYS' in record
    assert 'ASTRO-PH' in record
    assert 'Bob White' in record
    assert 'PhD' in record
    assert 'CERN' in record
    assert 'STAFF' in record
    assert '2000' in record
    assert '2001' in record
    holding_panel_author_detail.reject_record()


def test_accept_author(login):
    """Accept a submitted author"""
    create_author.go_to()
    create_author.submit_author(input_author_data)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(input_author_data)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(input_author_data)
    assert 'Accepted as Non-CORE' in holding_panel_author_detail.accept_record()


def test_reject_author(login):
    """Reject a submitted author"""
    create_author.go_to()
    create_author.submit_author(input_author_data)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(input_author_data)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(input_author_data)
    assert 'Rejected' in holding_panel_author_detail.reject_record()


def test_curation_author(login):
    """Accept with curation a submitted author"""
    create_author.go_to()
    create_author.submit_author(input_author_data)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(input_author_data)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(input_author_data)
    assert 'Accepted with Curation' in holding_panel_author_detail.curation_record()


def test_review_submission_author(login):
    """Review a submitted author"""
    create_author.go_to()
    create_author.submit_author(input_author_data)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(input_author_data)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(input_author_data)
    assert holding_panel_author_detail.review_record()
