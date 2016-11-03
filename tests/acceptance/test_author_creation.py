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
