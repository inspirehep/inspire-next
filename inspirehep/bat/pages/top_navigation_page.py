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

from os import environ

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..arsenic import Arsenic


def log_in(user_id, password):
    Arsenic().get(environ['SERVER_NAME'] + '/login/?local=1')
    Arsenic().find_element_by_id('email').send_keys(user_id)
    Arsenic().find_element_by_id('password').send_keys(password)
    Arsenic().find_element_by_xpath("//button[@type='submit']").click()


def log_out():
    WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'user-info')))
    Arsenic().find_element_by_id('user-info').click()
    Arsenic().find_element_by_xpath('(//button[@type="button"])[2]').click()


def am_i_logged():
    return (WebDriverWait(Arsenic(), 10).until(EC.visibility_of_element_located((By.ID, 'user-info'))).text == 'My account')
