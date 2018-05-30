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

"""Client interface for INSPIRE-MITMPROXY."""

from __future__ import absolute_import, division, print_function

from . import Session


class MITMClient(object):
    def __init__(self, proxy_host='http://mitm-manager.local'):
        self._client = Session(base_url=proxy_host)

    def set_scenario(self, scenario_name):
        self._client.put('/config', json={'active_scenario': scenario_name})

    def get_interactions_for_service(self, service_name):
        return self._client.get('/service/{}/interactions'.format(service_name)).json()

    def assert_interaction_used(self, service_name, interaction_name, times=None):
        interactions = self.get_interactions_for_service(service_name)
        num_calls = interactions.get(interaction_name, {}).get('num_calls', 0)

        if times is None and not num_calls:
            raise AssertionError(
                'Interaction %s in %s was not used' % (interaction_name, service_name)
            )

        if times is not None and num_calls != times:
            raise AssertionError(
                'Interaction %s in %s wasn\'t used %d times (but %d times instead)'
                % (interaction_name, service_name, times, num_calls)
            )
