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

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Arsenic(object):
    _instance = None

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args)
        return cls._instance

    def __init__(self, *args):
        if args:
            self.selenium = args[0]

    def write_in_autocomplete_field(self, field_id, field_value):
        self._instance.hide_title_bar()
        field = self._instance.find_element_by_id(field_id)
        field.send_keys(field_value)
        WebDriverWait(self._instance, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tt-suggestions")))
        field.send_keys(Keys.DOWN)
        field.send_keys(Keys.ENTER)
        self._instance.show_title_bar()
        return field.get_attribute('value')

    def hide_title_bar(self):
        self._instance.execute_script('document.getElementById("collections-section").style.display = "none"')
        self._instance.execute_script('document.getElementById("topnav").style.display = "none"')

    def show_title_bar(self):
        self._instance.execute_script('document.getElementById("collections-section").style.display = ""')
        self._instance.execute_script('document.getElementById("topnav").style.display = ""')

    def click_with_coordinates(self, element_id, x, y):
        el = self._instance.find_element_by_id(element_id)
        action = ActionChains(self._instance)
        action.move_to_element_with_offset(el, x, y)
        action.click()
        action.perform()

    def __getattr__(self, item):
        return getattr(self.selenium, item)


class ArsenicResponse(object):
    has_error = None

    def __init__(self, has_error):
        self.has_error = has_error
