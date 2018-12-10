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

import copy
import logging
import mock
import pytest

from fqn_decorators.decorators import get_fqn

from factories.db.invenio_records import TestRecordMetadata

from inspire_service_orcid.client import OrcidClient

from inspirehep.modules.orcid import (
    exceptions,
    domain_models,
)
from inspirehep.modules.orcid import cache as cache_module
from inspirehep.modules.orcid.cache import OrcidCache

from utils import override_config


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPusherCache(object):
    def setup(self):
        factory = TestRecordMetadata.create_from_file(__name__, 'test_orcid_models_TestOrcidPusher.json')
        self.record_metadata = factory.record_metadata
        self.inspire_record = factory.inspire_record
        self.orcid = '0000-0002-0942-3697'
        self.recid = factory.record_metadata.json['control_number']
        self.oauth_token = 'mytoken'
        self.cache = OrcidCache(self.orcid, self.recid)

        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = logging.CRITICAL

    def setup_method(self, method):
        cache_module.CACHE_PREFIX = get_fqn(method)

    def teardown(self):
        self.cache.delete_work_putcode()
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = 0
        cache_module.CACHE_PREFIX = None

    def test_record_not_found(self):
        with pytest.raises(exceptions.RecordNotFoundException):
            domain_models.OrcidPusher(self.orcid, 'notfound25697xxx', self.oauth_token)

    def test_push_cache_hit_content_not_changed(self):
        putcode = '00000'
        self.cache.write_work_putcode(putcode, self.inspire_record)

        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        result_putcode = pusher.push()
        assert result_putcode == putcode

    def test_push_force_cache_miss(self):
        putcode = '00000'
        self.record_metadata.json['_private_notes'] = [
            {'value': 'orcid-push-force-cache-miss'},
        ]
        self.cache.write_work_putcode(putcode, self.inspire_record)

        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        with mock.patch.object(OrcidClient, 'post_new_work') as mock_post_new_work:
            mock_post_new_work.return_value.__getitem__.return_value = '0000'
            pusher.push()
            mock_post_new_work.assert_called_once()

    def test_push_cache_hit_content_changed(self):
        putcode = '00000'
        cache_inspire_record = copy.deepcopy(self.inspire_record)
        cache_inspire_record['titles'][0]['title'] = 'foo'
        self.cache.write_work_putcode(putcode, cache_inspire_record)

        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        with mock.patch.object(OrcidClient, 'put_updated_work') as mock_put_updated_work:
            mock_put_updated_work.return_value.__getitem__.return_value = '0000'
            pusher.push()
        mock_put_updated_work.assert_called_once_with(mock.ANY, putcode)


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPusherPutUpdatedWork(object):
    def setup(self):
        factory = TestRecordMetadata.create_from_file(__name__, 'test_orcid_models_TestOrcidPusher.json')
        self.orcid = '0000-0002-0942-3697'
        self.recid = factory.record_metadata.json['control_number']
        self.inspire_record = factory.inspire_record
        self.cache = OrcidCache(self.orcid, self.recid)
        self.putcode = '46985330'
        self.cache.write_work_putcode(self.putcode)

        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = logging.CRITICAL

    @property
    def oauth_token(self):
        from flask import current_app  # Note: isolated_app not available in setup().
        # Pick the token from local inspirehep.cfg first.
        return current_app.config.get('ORCID_APP_LOCAL_TOKENS', {}).get(self.orcid, 'mytoken')

    def setup_method(self, method):
        cache_module.CACHE_PREFIX = get_fqn(method)

    def teardown(self):
        self.cache.delete_work_putcode()
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = 0
        cache_module.CACHE_PREFIX = None

    def test_push_updated_work_happy_flow(self):
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        result_putcode = pusher.push()
        assert result_putcode == int(self.putcode)
        assert not self.cache.has_work_content_changed(self.inspire_record)

    def test_push_updated_work_invalid_data_orcid(self):
        orcid = '0000-0002-0000-XXXX'
        self.cache = OrcidCache(orcid, self.recid)
        self.putcode = '46985330'
        self.cache.write_work_putcode(self.putcode)

        pusher = domain_models.OrcidPusher(orcid, self.recid, self.oauth_token)
        with pytest.raises(exceptions.InputDataInvalidException):
            pusher.push()

    def test_push_updated_work_invalid_data_token(self):
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, 'tokeninvalid')
        with pytest.raises(exceptions.InputDataInvalidException):
            pusher.push()

    def test_push_updated_work_invalid_data_putcode(self):
        self.cache.write_work_putcode('00000')

        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        with pytest.raises(exceptions.InputDataInvalidException):
            pusher.push()


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPusherPostNewWork(object):
    def setup(self):
        factory = TestRecordMetadata.create_from_file(__name__, 'test_orcid_models_TestOrcidPusherPostNewWork.json')
        self.orcid = '0000-0002-0942-3697'
        self.recid = factory.record_metadata.json['control_number']
        self.inspire_record = factory.inspire_record
        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = logging.CRITICAL

    @property
    def oauth_token(self):
        from flask import current_app  # Note: isolated_app not available in setup().
        # Pick the token from local inspirehep.cfg first.
        return current_app.config.get('ORCID_APP_LOCAL_TOKENS', {}).get(self.orcid, 'mytoken')

    @property
    def cache(self):
        return OrcidCache(self.orcid, self.recid)

    def setup_method(self, method):
        cache_module.CACHE_PREFIX = get_fqn(method)

    def teardown(self):
        self.cache.delete_work_putcode()
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = 0
        cache_module.CACHE_PREFIX = None

    def test_push_new_work_happy_flow(self):
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        result_putcode = pusher.push()
        assert result_putcode == 47160445
        assert not self.cache.has_work_content_changed(self.inspire_record)

    def test_push_new_work_invalid_data_orcid(self):
        orcid = '0000-0002-0000-XXXX'

        pusher = domain_models.OrcidPusher(orcid, self.recid, self.oauth_token)
        with pytest.raises(exceptions.InputDataInvalidException):
            pusher.push()

    def test_push_new_work_invalid_data_token(self):
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, 'tokeninvalid')
        with pytest.raises(exceptions.InputDataInvalidException):
            pusher.push()

    def test_push_new_work_invalid_data_xml(self):
        # Note: the recorded cassette returns (magically) a proper error.
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        with pytest.raises(exceptions.InputDataInvalidException):
            pusher.push()

    def test_push_new_work_already_existing(self):
        # ORCID_APP_CREDENTIALS is required because ORCID adds it as source_client_id_path.
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}):
            pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
            result_putcode = pusher.push()
        assert result_putcode == 47160445
        assert not self.cache.has_work_content_changed(self.inspire_record)

    def test_push_new_work_already_existing_with_recids(self):
        self.orcid = '0000-0002-5073-0816'
        self.cache.delete_work_putcode()
        # ORCID_APP_CREDENTIALS is required because ORCID adds it as source_client_id_path.
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}):
            pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
            result_putcode = pusher.push()
        assert result_putcode == 51346820
        assert not self.cache.has_work_content_changed(self.inspire_record)

    def test_push_new_work_already_existing_putcode_exception(self):
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        # ORCID_APP_CREDENTIALS is required because ORCID adds it as source_client_id_path.
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}), \
                pytest.raises(exceptions.PutcodeNotFoundInOrcidException):
            pusher.push()
        assert self.cache.has_work_content_changed(self.inspire_record)


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPusherDeleteWork(object):
    def setup(self):
        factory = TestRecordMetadata.create_from_file(__name__, 'test_orcid_models_TestOrcidPusherDeleteWork.json')
        self.orcid = '0000-0002-5073-0816'
        self.recid = factory.record_metadata.json['control_number']
        self.inspire_record = factory.inspire_record
        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = logging.CRITICAL
        self.cache.delete_work_putcode()

    @property
    def oauth_token(self):
        from flask import current_app  # Note: isolated_app not available in setup().
        # Pick the token from local inspirehep.cfg first.
        return current_app.config.get('ORCID_APP_LOCAL_TOKENS', {}).get(self.orcid, 'mytoken')

    @property
    def cache(self):
        return OrcidCache(self.orcid, self.recid)

    def setup_method(self, method):
        cache_module.CACHE_PREFIX = get_fqn(method)

    def teardown(self):
        self.cache.delete_work_putcode()
        logging.getLogger('inspirehep.modules.orcid.domain_models').disabled = 0
        cache_module.CACHE_PREFIX = None

    def test_delete_work_cache_miss(self):
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        # ORCID_APP_CREDENTIALS is required because ORCID adds it as source_client_id_path.
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}):
            assert not pusher.push()

    def test_delete_work_cache_hit(self):
        self.cache.write_work_putcode('51389857')
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        assert not pusher.push()

    def test_delete_work_cache_putcode_nonexisting(self):
        self.recid = '000000'
        TestRecordMetadata.create_from_kwargs(
            json={'control_number': self.recid, 'deleted': True})
        self.cache.write_work_putcode('51391229')
        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        assert not pusher.push()

    def test_delete_work_force_delete(self):
        self.recid = '99'
        TestRecordMetadata.create_from_kwargs(
            json={'control_number': self.recid,
                  'deleted': False,
                  '_private_notes': [{'value': 'orcid-push-force-delete'}]})
        self.cache.write_work_putcode('51391229')

        pusher = domain_models.OrcidPusher(self.orcid, self.recid, self.oauth_token)
        assert not pusher.push()
