# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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
from urlparse import urlparse


def handle_timeuot_exception(exc, arsenic, with_api):
    """Helper function to get some useful message on selenium timeout errors.
    """
    screenshot = arsenic.selenium.get_screenshot_as_base64()
    new_message = exc.message
    new_message += '\nPage Source:\n' + '#' * 20 + '\n' + arsenic.page_source
    new_message += '\nCurrent URL: %s\n' % arsenic.current_url
    new_message += '\nPage Screenshot base64:\n' + '#' * 20 + '\n' + screenshot
    if with_api:
        parsed_url = urlparse(arsenic.current_url)
        new_url = parsed_url._replace(path='/api' + parsed_url.path)
        arsenic.get(new_url.geturl())
        new_message += '\nAPI Page source:\n' + '#' * 20 + '\n' + arsenic.page_source

    raise exc.__class__(new_message)