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
from inspire_service_orcid import utils as inspire_service_orcid_utils

from inspirehep.modules.orcid.converter import ExternalIdentifier
from inspirehep.modules.records.utils import get_pid_from_record_uri
from . import exceptions, push_access_tokens, utils


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

    def get_all_inspire_putcodes_and_recids_iter(self):
        """
        Query ORCID api and get all the Inspire putcodes for the given ORCID.
        """
        summary_response = self._get_all_works_summary()
        # `putcodes_recids` is a list like: [('43326850', 20), ('43255490', None)]
        putcodes_recids = list(summary_response.get_putcodes_and_recids_for_source_iter(
            self.source_client_id_path))
        putcodes_with_recids = [x for x in putcodes_recids if x[1]]
        putcodes_without_recids = [x[0] for x in putcodes_recids if not x[1]]

        for putcode, recid in putcodes_with_recids:
            yield putcode, recid

        if not putcodes_without_recids:
            return

        for putcode, recid in self._get_putcodes_and_recids_iter(putcodes_without_recids):
            yield putcode, recid

    def _get_all_works_summary(self):
        """
        Query ORCID api and get all the putcodes with their embedded recids
        for the given ORCID.
        An embedded recid is a recid written as external-identifier.
        """
        response = self.client.get_all_works_summary()
        utils.log_service_response(logger, response, 'in OrcidPutcodeGetter works summary')
        try:
            response.raise_for_result()
        except (orcid_client_exceptions.TokenInvalidException,
                orcid_client_exceptions.TokenMismatchException,
                orcid_client_exceptions.TokenWithWrongPermissionException):
            logger.info('OrcidPutcodeGetter: deleting Orcid push access token={} for orcid={}'.format(
                self.oauth_token, self.orcid))
            push_access_tokens.delete_access_token(self.oauth_token, self.orcid)
            raise exceptions.TokenInvalidDeletedException
        except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
            raise exceptions.InputDataInvalidException(from_exc=exc)
        return response

    def _get_putcodes_and_recids_iter(self, putcodes):
        for putcode, url in self._get_urls_for_putcodes_iter(putcodes):
            # Filter out putcodes that do not belong to Inspire.
            if INSPIRE_WORK_URL_REGEX.match(url):
                recid = get_pid_from_record_uri(url)[1]
                if not recid:
                    logger.error('OrcidPutcodeGetter: cannot parse recid from url={} for orcid={}'.format(
                        url, self.orcid))
                    continue
                yield putcode, recid

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

    def get_putcodes_and_recids_by_identifiers_iter(self, identifiers):
        """
        Yield putcode and recid for each work matched by the external
        identifiers.
        Note: external identifiers of type 'other-id' are skipped.

        Args:
            identifiers (List[inspirehep.modules.orcid.converter.ExternalIdentifier]):
                list af all external identifiers added after the xml conversion.
        """
        summary_response = self._get_all_works_summary()
        for putcode, ids in summary_response.get_putcodes_and_external_identifiers_iter():
            # ids is a list like:
            #   [
            #       {'external-id-relationship': 'SELF',
            #        'external-id-type': 'other-id',
            #        'external-id-url': {'value': 'http://inspireheptest.cern.ch/record/20'},
            #        'external-id-value': '20'
            #       },...
            #   ]

            # Get the recid.
            recid = self._get_recid_for_work(ids, str(putcode))

            for identifier in ids:
                id_type = identifier.get('external-id-type')
                # We are interested only in doi, arxiv, isbns.
                if not id_type or id_type.lower() == 'other-id':
                    continue
                id_value = identifier.get('external-id-value')
                if not id_value:
                    continue

                if ExternalIdentifier(id_type, id_value) in identifiers:
                    yield putcode, recid

    def _get_recid_for_work(self, external_identifiers, putcode):
        """
        Get the recid for a work given its external identifiers and putcode.
        The recid might be in the external identifiers or a get_work_details()
        might be called to find it.

        Args:
            external_identifier (List[Dict]): a list like:
               [
                   {'external-id-relationship': 'SELF',
                    'external-id-type': 'other-id',
                    'external-id-url': {'value': 'http://inspireheptest.cern.ch/record/20'},
                    'external-id-value': '20'
                   },...
               ]
            putcode: putcode of the given work.

        Returns: the Inspire recid mathcing the work.
        """
        for identifier in external_identifiers:
            id_type = identifier.get('external-id-type')
            if not id_type or id_type.lower() != 'other-id':
                continue

            id_url = inspire_service_orcid_utils.smartget(identifier, 'external-id-url.value', '')
            if not re.match(r'.*inspire.*', id_url, re.I):
                continue

            id_value = identifier.get('external-id-value')
            if not id_value:
                continue

            # recid found.
            return id_value

        # The recid was not found in the external_identifiers.
        # Thus we call get_bulk_works_details_iter().
        putcodes_recid = list(self._get_putcodes_and_recids_iter([putcode]))

        if putcodes_recid:
            return putcodes_recid[0][1]
