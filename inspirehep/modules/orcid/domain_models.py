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

from flask import current_app
from time_execution import time_execution

from inspire_service_orcid import exceptions as orcid_client_exceptions
from inspire_service_orcid.client import OrcidClient

from inspirehep.utils.lock import distributed_lock
from inspirehep.utils.record_getter import (
    RecordGetterError,
    get_db_record,
)

from . import exceptions, utils
from .cache import OrcidCache
from .converter import OrcidConverter
from .putcode_getter import OrcidPutcodeGetter


logger = logging.getLogger(__name__)


class OrcidPusher(object):
    def __init__(self, orcid, recid, oauth_token):
        self.orcid = orcid
        self.recid = recid
        self.oauth_token = oauth_token

        try:
            self.inspire_record = get_db_record('lit', recid)
        except RecordGetterError as exc:
            raise exceptions.RecordNotFoundException(
                'recid={} not found for pid_type=lit'.format(self.recid),
                from_exc=exc)

        self.cache = OrcidCache(orcid, recid)
        self.lock_name = 'orcid:{}'.format(self.orcid)
        self.client = OrcidClient(self.oauth_token, self.orcid)
        self.xml_element = None

    @property
    def _do_force_cache_miss(self):
        """
        Hook to force a cache miss. This can be leveraged in feature tests.
        """
        for note in self.inspire_record.get('_private_notes', []):
            if note.get('value') == 'orcid-push-force-cache-miss':
                return True
        return False

    @time_execution
    def push(self):
        putcode = None
        if not self._do_force_cache_miss:
            putcode = self.cache.read_work_putcode()
            if not self.cache.has_work_content_changed(self.inspire_record):
                logger.info('OrcidPusher cache hit for recid={} and orcid={}'.format(
                    self.recid, self.orcid))
                return putcode
        logger.info('OrcidPusher cache miss for recid={} and orcid={}'.format(
            self.recid, self.orcid))

        self.xml_element = OrcidConverter(
            record=self.inspire_record,
            url_pattern=current_app.config['LEGACY_RECORD_URL_PATTERN'],
            put_code=putcode,
        ).get_xml(do_add_bibtex_citation=True)

        try:
            putcode = self._post_or_put_work(putcode)
        except orcid_client_exceptions.WorkAlreadyExistsException:
            # We POSTed the record as new work, but it failed because the work
            # already exists (identified by the external identifiers).
            # This means we do not have the putcode, thus we cache all
            # author's putcodes and PUT the work again.
            putcode = self._cache_all_author_putcodes()
            self._post_or_put_work(putcode)

        self.cache.write_work_putcode(putcode, self.inspire_record)
        return putcode

    @time_execution
    def _post_or_put_work(self, putcode=None):
        # Note: if putcode is None, then it's a POST (it means the work is new).
        # Otherwise a PUT (it means the work already exists and it has the given
        # putcode).

        # ORCID API allows 1 POST/PUT only for the same orcid at the same time.
        # Using `distributed_lock` to achieve this.
        with distributed_lock(self.lock_name, blocking=True):
            if putcode:
                response = self.client.put_updated_work(self.xml_element, putcode)
            else:
                response = self.client.post_new_work(self.xml_element)

        utils.log_service_response(logger, response, 'in OrcidPusher for recid={}'.format(self.recid))
        try:
            response.raise_for_result()
            putcode = response['putcode']
        except orcid_client_exceptions.WorkAlreadyExistsException:  # Only raisable by a POST.
            raise
        except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
            raise exceptions.InputDataInvalidException(from_exc=exc)
        return putcode

    @time_execution
    def _cache_all_author_putcodes(self):
        logger.info('New OrcidPusher cache all author putcodes for orcid={}'.format(self.orcid))
        putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
        putcodes_recids = list(putcode_getter.get_all_inspire_putcodes())  # Can raise exceptions.InputDataInvalidException.

        putcode = None
        for fetched_putcode, fetched_recid in putcodes_recids:
            if fetched_recid == str(self.recid):
                putcode = fetched_putcode
            cache = OrcidCache(self.orcid, fetched_recid)
            cache.write_work_putcode(fetched_putcode)

        if not putcode:
            raise exceptions.PutcodeNotFoundInOrcidException(
                'No putcode was found in ORCID API for orcid={} and recid={}.'
                ' And the POST has previously failed for the same recid because'
                ' the work had already existed'.format(self.orcid, self.recid))

        # Ensure the putcode is actually in cache.
        # Note: this step is not really necessary and it can be skipped, but
        # at this moment it helps isolate a potential issue.
        if not self.cache.read_work_putcode():
            raise exceptions.PutcodeNotFoundInCacheAfterCachingAllPutcodes(
                'No putcode={} found in cache for recid={} after having'
                ' cached all author putcodes for orcid={}'.format(
                    self.putcode, self.recid, self.orcid))

        return putcode
