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

from decorator import decorate
from os import environ

from . import Session


def with_mitmproxy(*args, **kwargs):
    '''Decorator to abstract fixture recording and scenario setup for the E2E tests with mitmproxy.

    Args:
        scenario_name (Optional[str]): scenario name, by default test name without 'test_' prefix

        should_record (Optional[bool]): is recording new interactions allowed during test run,
            by default `False`

        *args (List[Callable]): list of length of either zero or one: decorated function.
            This is to allow the decorator to function both with and without calling it
            with parameters: if args is present, we can deduce that the decorator was used
            without parameters.

    Returns:
        Callable: a decorator the can be used both with and without calling brackets
            (if all params should be default)
    '''
    scenario_name = kwargs.pop('scenario_name', None)
    should_record = kwargs.pop('should_record', False)

    if not args:
        assert not kwargs, 'Parameters %s not expected' % kwargs

    def _with_mitmproxy(func, *args, **kwargs):
        def ommit_test_in_name(name):
            if name.startswith('test_'):
                return name[5:]

        mitmproxy_url = environ.get('MITMPROXY_HOST', 'http://mitm-manager.local')
        mitm_client = MITMClient(mitmproxy_url)
        final_scenario_name = scenario_name or ommit_test_in_name(func.__name__)

        try:
            mitm_client.set_scenario(final_scenario_name)
            if should_record:
                mitm_client.start_recording()
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            mitm_client.stop_recording()
            mitm_client.set_scenario('default')

    def _decorator(func):
        return decorate(func, _with_mitmproxy)

    if args:
        return decorate(args[0], _with_mitmproxy)

    return _decorator


class MITMClient(object):
    def __init__(self, proxy_host='http://mitm-manager.local'):
        self._client = Session(base_url=proxy_host)

    def set_scenario(self, scenario_name):
        resp = self._client.put('/config', json={'active_scenario': scenario_name})
        resp.raise_for_status()

    def get_interactions_for_service(self, service_name):
        resp = self._client.get('/service/{}/interactions'.format(service_name))
        resp.raise_for_status()
        return resp.json()

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

    def start_recording(self):
        resp = self._client.post('/record', json={'enable': True})
        resp.raise_for_status()

    def stop_recording(self):
        resp = self._client.post('/record', json={'enable': False})
        resp.raise_for_status()
