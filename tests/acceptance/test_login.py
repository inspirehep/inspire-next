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

import os


def test_login(selenium, small_app):
    sign_in = selenium.find_element_by_link_text('Sign in')
    assert sign_in
    sign_in.click()
    assert 'Please sign in to suggest content to INSPIRE' in selenium.page_source
    selenium.get(os.environ['SERVER_NAME'] + '/login/?local=1')
    email = selenium.find_element_by_id('email')
    email.send_keys('admin@inspirehep.net')
    password = selenium.find_element_by_id('password')
    password.send_keys('123456')

