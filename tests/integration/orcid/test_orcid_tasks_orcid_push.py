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

from flask import current_app
from requests.exceptions import RequestException

from factories.db.invenio_records import TestRecordMetadata
from inspirehep.modules.orcid import exceptions
from inspirehep.modules.orcid.cache import OrcidCache
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
class TestOrcidPushRetryTask(object):
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
        exc = RequestException()
        exc.response = mock.Mock()
        exc.request = mock.Mock()
        self.mock_pusher.return_value.push.side_effect = exc

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


def get_local_access_tokens(orcid):
    # Pick the token from local inspirehep.cfg first.
    # This way you can store tokens in your local inspirehep.cfg (ignored
    # by git). This is handy when recording new episodes.
    local_tokens = current_app.config.get('ORCID_APP_LOCAL_TOKENS')
    if local_tokens:
        return local_tokens.get(orcid)
    return None


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPushTask(object):
    # NOTE: Only a few test here (1 happy flow and a few error flows). Exhaustive
    # testing is done in the domain model tests.
    def setup(self):
        factory = TestRecordMetadata.create_from_file(__name__, 'test_orcid_tasks_orcid_push_TestOrcidPush.json')
        self.orcid = '0000-0002-0942-3697'
        self.recid = factory.record_metadata.json['control_number']
        self.inspire_record = factory.inspire_record
        self.cache = OrcidCache(self.orcid, self.recid)
        self.oauth_token = get_local_access_tokens(self.orcid) or 'mytoken'

    def teardown(self):
        self.cache.delete_work_putcode()

    def test_push_new_work_happy_flow(self):
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*'):
            orcid_push(self.orcid, self.recid, self.oauth_token)
        assert not self.cache.has_work_content_changed(self.inspire_record)

    def test_push_new_work_invalid_data_orcid(self):
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*'), \
                pytest.raises(exceptions.InputDataInvalidException):
            orcid_push('0000-0002-0000-XXXX', self.recid, self.oauth_token)

    def test_push_new_work_already_existing(self):
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*',
                             ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}):
            orcid_push(self.orcid, self.recid, self.oauth_token)
        assert not self.cache.has_work_content_changed(self.inspire_record)
