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
    create_author,
    holding_panel_author_detail,
    holding_panel_author_list,
)


INPUT_AUTHOR_DATA = {
    'given_names': 'Mark',
    'family_name': 'Twain',
    'display_name': 'M. Twain',
    'native_name': 'M. Twain',
    'public_emails-0-email': 'mark.twain@history.org',
    'status': 'retired',
    'orcid': '1111-1111-1111-1111',
    'websites-0-webpage': 'http://www.example1.com',
    'websites-1-webpage': 'http://www.example2.com',
    'linkedin_url': 'http://www.example3.com',
    'twitter_url': 'http://www.example4.com',
    'blog_url': 'http://www.example5.com',
    'institution_history-0-name': 'CERN',
    'institution_history-0-start_year': '2000',
    'institution_history-0-end_year': '2001',
    'institution_history-0-rank': 'STAFF',
    'experiments-0-name': 'ATLAS',
    'experiments-0-start_year': '2002',
    'experiments-0-end_year': '2005',
    'advisors-0-name': 'Bob White',
    'advisors-0-degree_type': 'habilitation',
    'extra_comments': 'Some comments about the author',
    'field-research_field': 'astro-ph, cond-mat'
}


def test_institutions_typeahead(login):
    create_author.go_to()
    create_author.write_institution('cer', 'CERN').assert_no_errors()


def test_experiments_typehead(login):
    create_author.go_to()
    create_author.write_experiment('atl', 'ATLAS').assert_no_errors()


def test_advisors_typehead(login):
    create_author.go_to()
    create_author.write_advisor('alexe', 'Vorobyev, Alexey').assert_no_errors()


def test_mail_format(login):
    create_author.go_to()
    create_author.write_mail('wrong.mail').assert_no_errors()
    create_author.write_mail('me@me.com').assert_errors()


def test_ORCID_format(login):
    create_author.go_to()
    create_author.write_orcid('wrong.ORCID').assert_no_errors()
    create_author.write_orcid('1111-1111-1111-1111').assert_errors()


def test_institutions_years(login):
    create_author.go_to()

    input_id = 'institution_history-0-start_year'
    error_mess_id = 'state-institution_history-0-start_year'
    create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).assert_no_errors()
    create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).assert_errors()

    input_id = 'institution_history-0-end_year'
    error_mess_id = 'state-institution_history-0-end_year'
    create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).assert_no_errors()
    create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).assert_errors()


def test_experiments_years(login):
    create_author.go_to()

    input_id = 'experiments-0-start_year'
    error_mess_id = 'state-experiments-0-start_year'
    create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).assert_no_errors()
    create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).assert_errors()

    input_id = 'experiments-0-end_year'
    error_mess_id = 'state-experiments-0-end_year'
    create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).assert_no_errors()
    create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).assert_errors()


def test_mandatory_fields(login):
    expected_data = {
        'given-name': 'This field is required.',
        'display-name': 'This field is required.',
        'reserach-field': 'This field is required.'
    }

    create_author.go_to()
    create_author.submit_empty_form(expected_data).assert_no_errors()


def test_submit_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA).assert_no_errors()

    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(
        INPUT_AUTHOR_DATA
    ).assert_no_errors()

    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(
        INPUT_AUTHOR_DATA
    ).assert_no_errors()
    holding_panel_author_detail.reject_record()


def test_accept_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.accept_record().assert_no_errors()


def test_reject_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.reject_record().assert_no_errors()


def test_curation_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.curation_record().assert_no_errors()


def test_review_submission_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.review_record(INPUT_AUTHOR_DATA).assert_no_errors()
