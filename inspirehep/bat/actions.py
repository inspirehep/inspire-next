# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017-2018 CERN.
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

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from inspire_utils.helpers import force_list

from inspirehep.bat.arsenic import Arsenic
from inspirehep.bat.EC import GetText, TryClick


def _parse_selectors(_id=None, xpath=None, link_text=None):
    if not _id and not xpath and not link_text:
        raise TypeError('No _id, xpath nor link_text passed, one is needed.')

    if _id:
        by = By.ID
        value = _id

    if xpath:
        by = By.XPATH
        value = xpath

    if link_text:
        by = By.LINK_TEXT
        value = link_text

    return by, value


def wait_for(_id=None, xpath=None, link_text=None):
    by, value = _parse_selectors(_id=_id, xpath=xpath, link_text=link_text)
    return WebDriverWait(Arsenic(), 10).until(
        EC.visibility_of_element_located((by, value))
    )


def click(_id=None, xpath=None, link_text=None):
    by, value = _parse_selectors(_id=_id, xpath=xpath, link_text=link_text)
    return WebDriverWait(Arsenic(), 10).until(TryClick((by, value)))


def write(data, _id=None, xpath=None, link_text=None):
    data = force_list(data)
    elem = wait_for(_id=_id, xpath=xpath, link_text=link_text)
    return elem.send_keys(*data)

def get_text_of(_id=None, xpath=None, link_text=None):
    by, value = _parse_selectors(_id=_id, xpath=xpath, link_text=link_text)
    return WebDriverWait(Arsenic(), 10).until(GetText((by, value)))


def get_value_of(_id=None, xpath=None, link_text=None):
    elem = wait_for(_id=_id, xpath=xpath, link_text=link_text)
    return elem.get_attribute('value')


def select(value, _id=None, xpath=None, link_text=None):
    elem = wait_for(_id=_id, xpath=xpath, link_text=link_text)
    return Select(elem).select_by_value(value)
