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

import itertools
import logging
import re

from flask import current_app

from inspire_service_orcid import exceptions as orcid_client_exceptions
from inspire_service_orcid.client import OrcidClient

from . import exceptions, utils


INSPIRE_WORK_URL_REGEX = re.compile(
    r'https?://(?:labs\.)?inspirehep\.net/(?:record|literature)/(\d+)',
    re.IGNORECASE
)


logger = logging.getLogger(__name__)


class OrcidPutcodeGetter(object):
    def __init__(self, orcid, oauth_token):
        self.orcid = orcid
        self.oauth_token = oauth_token
        self.client = OrcidClient(self.oauth_token, self.orcid)
        self.source_client_id_path = current_app.config['ORCID_APP_CREDENTIALS'][
            'consumer_key']

    def get_all_inspire_putcodes(self):
        """
        Get all the Inspire putcodes for the given ORCID.
        """
        putcodes = self._get_all_putcodes()
        if not putcodes:
            return
        # Filter out putcodes that do not belong to Inspire.
        for putcode, url in self._get_urls_for_putcodes(putcodes):
            if INSPIRE_WORK_URL_REGEX.match(url):
                yield putcode, url

    def _get_all_putcodes(self):
        response = self.client.get_all_works_summary()
        utils.log_service_response(logger, response, 'in OrcidPutcodeGetter works summary')
        try:
            response.raise_for_result()
        except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
            raise exceptions.InputDataInvalidException(from_exc=exc)
        return list(response.get_putcodes_for_source(self.source_client_id_path))

    def _get_urls_for_putcodes(self, putcodes):
        # The call get_bulk_works_details() can be very expensive for an
        # author with many works (if each work also has many *contributors*).
        # Fi. for an ATLAS author with ~750 works, 8 calls would be performed
        # with a total data transfer > 0.5 Gb.
        chained = []
        for response in self.client.get_bulk_works_details(putcodes):
            utils.log_service_response(logger, response, 'in OrcidPutcodeGetter works details')
            try:
                response.raise_for_result()
            except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
                raise exceptions.InputDataInvalidException(from_exc=exc)

            chained = itertools.chain(chained, response.get_putcodes_and_urls())
        return chained
