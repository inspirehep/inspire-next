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

import os
from time import sleep

from selenium.webdriver.common.keys import Keys


def test_institutions_typehead(selenium, login):
    """"Test the suggestions in the istitutions field"""
    selenium.get(os.environ['SERVER_NAME'] + '/submit/author/create')
    institution_field = selenium.find_element_by_id("institution_history-0-name")
    force_autocomplete_event(institution_field, "CER")
    assert 'CERN' in institution_field.get_attribute("value")


def force_autocomplete_event(field, chunk_text):
    """Performs selection in a html text field"""
    field.send_keys(chunk_text)
    sleep(2)
    field.send_keys(Keys.DOWN)
    field.send_keys(Keys.ENTER)
