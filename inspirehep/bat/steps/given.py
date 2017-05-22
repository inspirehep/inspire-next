# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

import os

from pytest_bdd import given

from inspirehep.bat.arsenic import Arsenic
from inspirehep.bat.locators import LoginPageLocators as LP


@given('I am logged in')
def login_and_out():
    def _log_in(user_id, password):
        Arsenic().get(os.environ['SERVER_NAME'] + '/login/?local=1')
        Arsenic().get_element_with_locator(LP.EMAIL_TEXT_BOX).send_keys(user_id)
        Arsenic().get_element_with_locator(LP.PASSW_TEXT_BOX).send_keys(password)
        Arsenic().get_element_with_locator(LP.SUBMIT_BUTTON).click()

    def _log_out():
        Arsenic().get_element_with_locator(LP.PROFILE_BUTTON).click()
        Arsenic().get_element_with_locator(LP.LOG_OUT_BUTTON).click()

    _log_in('admin@inspirehep.net', '123456')
    yield
    _log_out()
