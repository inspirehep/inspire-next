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
import pytest

from inspirehep.modules.orcid import exceptions
from inspirehep.modules.orcid.putcode_getter import OrcidPutcodeGetter

from utils import override_config


@pytest.mark.usefixtures('isolated_app')
class TestOrcidPutcodeGetter(object):
    def setup(self):
        self.orcid = '0000-0002-6665-4934'  # ATLAS author.
        from flask import current_app  # Note: isolated_app not available in setup().
        # Pick the token from local inspirehep.cfg first.
        self.oauth_token = current_app.config['ORCID_APP_CREDENTIALS'].get('oauth_tokens', {}).get(self.orcid, 'mytoken')
        self.source_client_id_path = '0000-0001-8607-8906'

        # Disable logging.
        logging.getLogger('inspirehep.modules.orcid.putcode_getter').disabled = logging.CRITICAL

    def teardown(self):
        logging.getLogger('inspirehep.modules.orcid.putcode_getter').disabled = 0

    def test_get_all_inspire_putcodes_happy_flow(self):
        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': self.source_client_id_path}):
            putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
            putcodes_urls = list(putcode_getter.get_all_inspire_putcodes())
        assert len(putcodes_urls) == 297
        for _, url in putcodes_urls:
            assert 'http://inspirehep.net' in url

    def test_token_invalid(self):
        putcode_getter = OrcidPutcodeGetter(self.orcid, 'invalid')
        with pytest.raises(exceptions.InputDataInvalidException):
            list(putcode_getter.get_all_inspire_putcodes())

    def test_putcode_not_found(self, isolated_app):
        orcid = '0000-0002-0942-3697'
        oauth_token = isolated_app.config['ORCID_APP_CREDENTIALS'].get('oauth_tokens', {}).get(orcid, 'mytoken')

        with override_config(ORCID_APP_CREDENTIALS={'consumer_key': self.source_client_id_path}):
            putcode_getter = OrcidPutcodeGetter(orcid, oauth_token)
            with pytest.raises(exceptions.InputDataInvalidException):
                list(putcode_getter.get_all_inspire_putcodes())
