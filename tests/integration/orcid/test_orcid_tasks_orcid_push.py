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

from __future__ import absolute_import, division, print_function

import logging
import mock
import pytest
import re

from requests.exceptions import RequestException

from inspirehep.modules.orcid.tasks import orcid_push

from utils import override_config


class TestFeatureFlagOrcidPushWhitelistRegex(object):
    def test_whitelist_regex_none(self):
        FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '^$'

        compiled = re.compile(FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX)
        assert not re.match(compiled, '0000-0002-7638-5686')
        assert not re.match(compiled, 'foo')
        # Be careful with the empty string.
        assert re.match(compiled, '')

    def test_whitelist_regex_any(self):
        FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '.*'

        compiled = re.compile(FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX)
        assert re.match(compiled, '0000-0002-7638-5686')
        assert re.match(compiled, 'foo')
        assert re.match(compiled, '')

    def test_whitelist_regex_some(self):
        FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX = '^(0000-0002-7638-5686|0000-0002-7638-5687)$'

        compiled = re.compile(FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX)
        assert re.match(compiled, '0000-0002-7638-5686')
        assert not re.match(compiled, '0000-0002-7638-5686XX')
        assert not re.match(compiled, '0000-0002-7638-56')
        assert not re.match(compiled, '0000-0002-7638-5689')
        assert not re.match(compiled, 'foo')
        assert not re.match(compiled, '')


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPushFeatureFlag(object):
    def setup(self):
        self._patcher = mock.patch('inspirehep.modules.orcid.domain_models.OrcidPusher')
        self.mock_pusher = self._patcher.start()

        self.orcid = '0000-0002-7638-5686'
        self.recid = 'myrecid'
        self.oauth_token = 'mytoken'

        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.tasks').disabled = logging.CRITICAL

    def teardown(self):
        self._patcher.stop()
        logging.getLogger('inspirehep.modules.orcid.tasks').disabled = 0

    def test_main_feature_flag(self):
        regex = '.*'
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=False,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX=regex):
            orcid_push(self.orcid, self.recid, self.oauth_token)

        self.mock_pusher.assert_not_called()

    def test_whitelist_regex_any(self):
        regex = '.*'
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX=regex):
            orcid_push(self.orcid, self.recid, self.oauth_token)

        self.mock_pusher.assert_called_once_with(self.orcid, self.recid, self.oauth_token)

    def test_whitelist_regex_none(self):
        regex = '^$'
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX=regex):
            orcid_push(self.orcid, self.recid, self.oauth_token)

        self.mock_pusher.assert_not_called()

    def test_whitelist_regex_some(self):
        regex = '^(0000-0002-7638-5686|0000-0002-7638-5687)$'
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX=regex):
            orcid_push(self.orcid, self.recid, self.oauth_token)

            self.mock_pusher.assert_called_once_with(self.orcid, self.recid, self.oauth_token)


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPush(object):
    def setup(self):
        self._patcher = mock.patch('inspirehep.modules.orcid.domain_models.OrcidPusher')
        self.mock_pusher = self._patcher.start()

        self.orcid = '0000-0002-7638-5686'
        self.recid = 'myrecid'
        self.oauth_token = 'mytoken'

        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.tasks').disabled = logging.CRITICAL

    def teardown(self):
        self._patcher.stop()
        logging.getLogger('inspirehep.modules.orcid.tasks').disabled = 0

    def test_happy_flow(self):
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*'):
            orcid_push(self.orcid, self.recid, self.oauth_token)

        self.mock_pusher.assert_called_once_with(self.orcid, self.recid, self.oauth_token)
        self.mock_pusher.return_value.push.assert_called_once()

    def test_retry_triggered(self):
        self.mock_pusher.return_value.push.side_effect = RequestException

        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*'), \
                mock.patch('inspirehep.modules.orcid.tasks.orcid_push.retry', side_effect=RequestException) as mock_orcid_push_task_retry, \
                pytest.raises(RequestException):
            orcid_push(self.orcid, self.recid, self.oauth_token)

        self.mock_pusher.assert_called_once_with(self.orcid, self.recid, self.oauth_token)
        self.mock_pusher.return_value.push.assert_called_once()
        mock_orcid_push_task_retry.assert_called_once()

    def test_retry_not_triggered(self):
        self.mock_pusher.return_value.push.side_effect = IOError

        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*'), \
                mock.patch('inspirehep.modules.orcid.tasks.orcid_push.retry') as mock_orcid_push_task_retry, \
                pytest.raises(IOError):
            orcid_push(self.orcid, self.recid, self.oauth_token)

        self.mock_pusher.assert_called_once_with(self.orcid, self.recid, self.oauth_token)
        self.mock_pusher.return_value.push.assert_called_once()
        mock_orcid_push_task_retry.assert_not_called()
