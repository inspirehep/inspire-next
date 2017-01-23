# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import mock

from inspirehep.utils.url import make_user_agent_string

@mock.patch('inspirehep.utils.url.current_app')
@mock.patch('inspirehep.utils.url.__version__', '0.1.0')
def test_make_user_agent_string(current_app, app):
    """Test that user agent is created."""
    current_app.config = {'SERVER_NAME': 'http://inspirehep.net'}

    with app.app_context():
        user_agent = make_user_agent_string()
        assert user_agent == "InspireHEP-0.1.0 (+http://inspirehep.net;)"

        user_agent_with_component = make_user_agent_string("submission")
        assert user_agent_with_component == "InspireHEP-0.1.0 (+http://inspirehep.net;) [submission]"
