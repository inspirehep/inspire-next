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

from pytest_bdd import when, parsers

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

from inspirehep.bat.arsenic import Arsenic


@when(parsers.cfparse('I click on the button with id {button_id}'))
def click_generic_button(button_id):
    WebDriverWait(Arsenic(), 2).until(
        EC.visibility_of_element_located((By.ID, button_id))
    ).click()


@when(parsers.cfparse('I click on the link with text {text_value}'))
def click_generic_link_button(text_value):
    Arsenic().find_element_by_link_text(text_value).click()


@when(parsers.cfparse('I select the value {input_select} in the select box with id {field_id}'))
def select_generic_value(input_select, field_id):
    Select(Arsenic().find_element_by_id(field_id)).select_by_value(input_select)


@when(parsers.cfparse('I insert <input> in the input box with id {field_id}'))
@when(parsers.cfparse('I insert {input} in the input box with id {field_id}'))
def write_in_a_generic_field(input, field_id):
    Arsenic().write_in_generic_field(field_id, input)


@when(
    parsers.cfparse(
        'I insert {input_autocompletion} in the autocomplete input box with id {autocompletion_field}'
    )
)
def write_in_a_generic_autocompletion_field(input_autocompletion, autocompletion_field):
    Arsenic().write_in_autocomplete_field(autocompletion_field, input_autocompletion)
