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

from inspirehep.modules.records.utils import get_pid_from_record_uri
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

    def get_all_inspire_putcodes_iter(self):
        """
        Query ORCID api and get all the Inspire putcodes for the given ORCID.
        """
        # `putcodes_recids` is a list like: [('43326850', 20), ('43255490', None)]
        putcodes_recids = self._get_all_putcodes_and_recids()
        putcodes_with_recids = [x for x in putcodes_recids if x[1]]
        putcodes_without_recids = [x[0] for x in putcodes_recids if not x[1]]

        for putcode, recid in putcodes_with_recids:
            yield putcode, recid

        if not putcodes_without_recids:
            return

        # Filter out putcodes that do not belong to Inspire.
        for putcode, url in self._get_urls_for_putcodes_iter(putcodes_without_recids):
            if INSPIRE_WORK_URL_REGEX.match(url):
                recid = get_pid_from_record_uri(url)[1]
                if not recid:
                    logger.error('OrcidPutcodeGetter: cannot parse recid from url={} for orcid={}'.format(
                        url, self.orcid))
                    continue
                yield putcode, recid

    def _get_all_putcodes_and_recids(self):
        response = self.client.get_all_works_summary()
        utils.log_service_response(logger, response, 'in OrcidPutcodeGetter works summary')
        try:
            response.raise_for_result()
        except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
            raise exceptions.InputDataInvalidException(from_exc=exc)
        return list(response.get_putcodes_and_recids_for_source_iter(self.source_client_id_path))

    def _get_urls_for_putcodes_iter(self, putcodes):
        # The call `get_bulk_works_details_iter()` can be expensive for an
        # author with many works (if each work also has many *contributors*).
        # Fi. for an ATLAS author with ~750 works (each of them with many
        # authors), 8 calls would be performed with a total data transfer > 0.5 Gb.
        chained = []
        for response in self.client.get_bulk_works_details_iter(putcodes):
            # Note: this log can be large. Consider removing it when this part
            # is considered mature.
            utils.log_service_response(logger, response, 'in OrcidPutcodeGetter works details')
            try:
                response.raise_for_result()
            except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
                raise exceptions.InputDataInvalidException(from_exc=exc)

            chained = itertools.chain(chained, response.get_putcodes_and_urls_iter())
        return chained
