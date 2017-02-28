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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
"""Module for custom selenium 'Expected Conditions'.

See Also:
    http://selenium-python.readthedocs.io/waits.html

"""
from __future__ import absolute_import, division, print_function

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException


class TryClick(object):
    """ An Expectation that tries to click an element.

    Is very similar to `EC.element_to_be_clickable`, but actually works.

    Todo:
        Better filter out the `WebDriverException`s.
    """
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = EC.visibility_of_element_located(self.locator)(driver)
        if not element:
            return False

        try:
            element.click()
        except WebDriverException:
            return False

        return element
