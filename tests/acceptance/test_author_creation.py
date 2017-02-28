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

from __future__ import absolute_import, division, print_function

from inspirehep.bat.pages import (
    create_author,
    holding_panel_author_detail,
    holding_panel_author_list,
)


INPUT_AUTHOR_DATA = {
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
    'extra_comments': 'Some comments about the author',
    'subject-0': 'ACC-PHYS',
    'subject-1': 'ASTRO-PH'
}


def test_institutions_typeahead(login):
    create_author.go_to()
    assert create_author.write_institution('cer', 'CERN').has_error()


def test_experiments_typehead(login):
    create_author.go_to()
    assert create_author.write_experiment('atl', 'ATLAS').has_error()


def test_advisors_typehead(login):
    create_author.go_to()
    assert create_author.write_advisor('alexe', 'Vorobyev, Alexey').has_error()


def test_mail_format(login):
    create_author.go_to()
    assert create_author.write_mail('wrong.mail').has_error()
    assert not create_author.write_mail('me@me.com').has_error()


def test_ORCID_format(login):
    create_author.go_to()
    assert create_author.write_orcid('wrong.ORCID').has_error()
    assert not create_author.write_orcid('1111-1111-1111-1111').has_error()


def test_institutions_years(login):
    create_author.go_to()

    input_id = 'institution_history-0-start_year'
    error_mess_id = 'state-institution_history-0-start_year'
    assert create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).has_error()
    assert not create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).has_error()

    input_id = 'institution_history-0-end_year'
    error_mess_id = 'state-institution_history-0-end_year'
    assert create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).has_error()
    assert not create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).has_error()


def test_experiments_years(login):
    create_author.go_to()

    input_id = 'experiments-0-start_year'
    error_mess_id = 'state-experiments-0-start_year'
    assert create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).has_error()
    assert not create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).has_error()

    input_id = 'experiments-0-end_year'
    error_mess_id = 'state-experiments-0-end_year'
    assert create_author.write_year(
        input_id,
        error_mess_id,
        'wrongyear',
    ).has_error()
    assert not create_author.write_year(
        input_id,
        error_mess_id,
        '2016',
    ).has_error()


def test_mandatory_fields(login):
    expected_data = {
        'given-name': 'This field is required.',
        'display-name': 'This field is required.',
        'reserach-field': 'This field is required.'
    }

    create_author.go_to()
    assert create_author.submit_empty_form(expected_data).has_error()


def test_submit_author(login):
    create_author.go_to()
    assert create_author.submit_author(INPUT_AUTHOR_DATA).has_error()

    holding_panel_author_list.go_to()
    assert holding_panel_author_list.load_submission_record(
        INPUT_AUTHOR_DATA
    ).has_error()

    holding_panel_author_detail.go_to()
    assert holding_panel_author_detail.load_submitted_record(
        INPUT_AUTHOR_DATA
    ).has_error()
    holding_panel_author_detail.reject_record()


def test_accept_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    assert holding_panel_author_detail.accept_record().has_error()


def test_reject_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    assert holding_panel_author_detail.reject_record().has_error()


def test_curation_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    assert holding_panel_author_detail.curation_record().has_error()


def test_review_submission_author(login):
    create_author.go_to()
    create_author.submit_author(INPUT_AUTHOR_DATA)
    holding_panel_author_list.go_to()
    holding_panel_author_list.load_submission_record(INPUT_AUTHOR_DATA)
    holding_panel_author_detail.go_to()
    holding_panel_author_detail.load_submitted_record(INPUT_AUTHOR_DATA)
    assert holding_panel_author_detail.review_record().has_error()
