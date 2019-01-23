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

from inspirehep.modules.orcid import exceptions
from inspirehep.modules.orcid.converter import ExternalIdentifier
from inspirehep.modules.orcid.putcode_getter import OrcidPutcodeGetter

from utils import override_config


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPutcodeGetter(object):
    def setup(self):
        self.orcid = '0000-0002-6665-4934'  # ATLAS author.
        self.source_client_id_path = '0000-0001-8607-8906'
        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.putcode_getter').disabled = logging.CRITICAL

    @property
    def oauth_token(self):
        from flask import current_app  # Note: isolated_app not available in setup().
        # Pick the token from local inspirehep.cfg first.
        return current_app.config.get('ORCID_APP_LOCAL_TOKENS', {}).get(self.orcid, 'mytoken')

    def teardown(self):
        logging.getLogger('inspirehep.modules.orcid.putcode_getter').disabled = 0

    def test_get_all_inspire_putcodes_happy_flow(self):
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': self.source_client_id_path}):
            putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
            putcodes_recids = list(putcode_getter.get_all_inspire_putcodes_and_recids_iter())
        assert len(putcodes_recids) == 297
        for _, recid in putcodes_recids:
            assert int(recid)

    def test_get_all_inspire_putcodes_with_recids(self):
        self.orcid = '0000-0002-5073-0816'
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': self.source_client_id_path}):
            putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
            putcodes_recids = list(putcode_getter.get_all_inspire_putcodes_and_recids_iter())
        assert putcodes_recids == [('51341099', '20'), ('51341192', '20')]

    def test_token_invalid(self):
        token = 'invalid'
        putcode_getter = OrcidPutcodeGetter(self.orcid, token)
        with pytest.raises(exceptions.TokenInvalidDeletedException), \
                mock.patch('inspirehep.modules.orcid.push_access_tokens.delete_access_token') as mock_delete_access_token:
                list(putcode_getter.get_all_inspire_putcodes_and_recids_iter())
        mock_delete_access_token.assert_called_once_with(token, self.orcid)

    def test_putcode_not_found(self):
        self.orcid = '0000-0002-0942-3697'
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': self.source_client_id_path}):
            putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
            with pytest.raises(exceptions.InputDataInvalidException):
                list(putcode_getter.get_all_inspire_putcodes_and_recids_iter())

    def test_get_putcodes_and_recids_by_identifiers_iter(self, ):
        self.orcid = '0000-0002-0942-3697'
        id_doi1 = ExternalIdentifier('doi', '10.1000/test.orcid.push')
        id_doi2 = ExternalIdentifier('doi', '10.1000/orcid-test-andrea-rossoni')
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': self.source_client_id_path}):
            putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
            putcodes_recids = list(putcode_getter.get_putcodes_and_recids_by_identifiers_iter([id_doi1, id_doi2]))
        assert putcodes_recids == [(51548299, '999'), (51344802, '1680808')]
