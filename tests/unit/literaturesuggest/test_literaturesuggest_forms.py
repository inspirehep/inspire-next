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

from inspirehep.modules.literaturesuggest.forms import CheckboxButton

from mock import Mock


def test_checkbox_button_handles_unicode_message():
    unicode_message = u'φοο'
    mocked_field = Mock()
    mocked_field.id = 'welcome'
    mocked_field.default = 'Welcome!'

    checkbox_button = CheckboxButton(unicode_message)

    expected_html = u'<div id="field-welcome">' \
        u'<label for="welcome">' \
        u'<input class="checkbox-ok-upload" name="welcome" type="checkbox" value="Welcome!">' \
        u'<strong><em>φοο</em></strong><small>&nbsp;(temporary text)</small>' \
        u'</label>' \
        u'</div>'

    assert checkbox_button(mocked_field) == expected_html
