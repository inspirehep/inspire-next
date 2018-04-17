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

import os

from selenium.common.exceptions import (
    ElementNotVisibleException,
    WebDriverException,
)

from inspirehep.bat.arsenic import Arsenic
from inspirehep.bat.actions import click, get_text_of


FIRST_RECORD = '//div[@class="row hp-item ng-scope"][1]'
FIRST_RECORD_DETAILS = (
    FIRST_RECORD + '/div/div/div[2]/holding-pen-template-handler'
)
FIRST_RECORD_TITLE = FIRST_RECORD_DETAILS + '/h4/a'
FIRST_RECORD_SHOW_ABSTRACT_LINK = '//div[@class="abstract ng-scope"]/a'


def go_to():
    Arsenic().get(
        os.environ['SERVER_NAME'] +
        '/holdingpen/list/?page=1&size=10&workflow_name=HEP'
    )


def get_first_record_info(try_count=0):
    def _refresh_and_retry(try_count):
        Arsenic().refresh()
        return get_first_record_info(try_count=try_count)

    try:
        click(xpath=FIRST_RECORD_SHOW_ABSTRACT_LINK)
        record = get_text_of(xpath=FIRST_RECORD)
    except (ElementNotVisibleException, WebDriverException):
        try_count += 1
        if try_count >= 15:
            raise
        record = _refresh_and_retry(try_count=try_count)

    if 'Waiting' in record:
        try_count += 1
        if try_count >= 15:
            raise Exception(
                'Timed out waiting for record to get out of Waiting status.'
            )
        return _refresh_and_retry(try_count=try_count)

    return record


def click_first_record():
    click(xpath=FIRST_RECORD_TITLE)


def assert_first_record_matches(input_data):
    record = get_first_record_info()

    for author in input_data.authors:
        for name_part in author['name'].split():
            assert name_part in record

    for subject in input_data.subjects:
        assert subject in record

    assert input_data.title in record
    assert 'admin@inspirehep.net' in record
    assert input_data.abstract in record


def assert_first_record_completed():
    record = get_first_record_info()
    assert 'Completed' in record
