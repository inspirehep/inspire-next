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

import pytest


def test_literature(selenium):
    selenium.find_element_by_link_text('Literature').click()
    assert 'Search 426 articles' in selenium.page_source
    search_button = selenium.find_element_by_id('search-form-button').click()
    assert 'Found 426 results.' in selenium.page_source


def test_authors(selenium):
    selenium.find_element_by_link_text('Authors').click()
    assert 'Search 100 authors' in selenium.page_source
    search_button = selenium.find_element_by_id('search-form-button').click()
    assert 'Found 100 results.' in selenium.page_source


@pytest.mark.xfail(reason='we need first to implement integration of data')
def test_data(selenium):
    selenium.find_element_by_link_text('Data').click()
    assert 'Search 100 data sets' in selenium.page_source
    search_button = selenium.find_element_by_id('search-form-button').click()
    assert 'Found 100 results.' in selenium.page_source


def test_jobs(selenium):
    # Jobs jump automatically to the open jobs
    selenium.find_element_by_link_text('Jobs').click()
    assert 'Found 10 results.' in selenium.page_source


def test_institutions(selenium):
    selenium.find_element_by_link_text('Institutions').click()
    assert 'Search 10 institutions' in selenium.page_source
    search_button = selenium.find_element_by_id('search-form-button').click()
    assert 'Found 10 results.' in selenium.page_source


def test_experiments(selenium):
    selenium.find_element_by_link_text('Experiments').click()
    assert 'Search 10 experiments' in selenium.page_source
    search_button = selenium.find_element_by_id('search-form-button').click()
    assert 'Found 10 results.' in selenium.page_source


def test_journals(selenium):
    selenium.find_element_by_link_text('Journals').click()
    assert 'Search 10 journals' in selenium.page_source
    search_button = selenium.find_element_by_id('search-form-button').click()
    assert 'Found 10 results.' in selenium.page_source
