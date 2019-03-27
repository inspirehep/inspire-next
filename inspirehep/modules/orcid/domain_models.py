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

from . import exceptions, push_access_tokens, utils
from .cache import OrcidCache
from .converter import OrcidConverter
from .putcode_getter import OrcidPutcodeGetter


logger = logging.getLogger(__name__)


class OrcidPusher(object):
    def __init__(self, orcid, recid, oauth_token,
                 do_fail_if_duplicated_identifier=False, record_db_version=None):
        self.orcid = orcid
        self.recid = recid
        self.oauth_token = oauth_token
        self.do_fail_if_duplicated_identifier = do_fail_if_duplicated_identifier
        self.record_db_version = record_db_version
        self.inspire_record = self._get_inspire_record()
        self.cache = OrcidCache(orcid, recid)
        self.lock_name = 'orcid:{}'.format(self.orcid)
        self.client = OrcidClient(self.oauth_token, self.orcid)
        self.converter = None

    @time_execution
    def _get_inspire_record(self):
        try:
            inspire_record = get_db_record('lit', self.recid)
        except RecordGetterError as exc:
            raise exceptions.RecordNotFoundException(
                'recid={} not found for pid_type=lit'.format(self.recid),
                from_exc=exc)

        # If the record_db_version was given, then ensure we are about to push
        # the right record version.
        # This check is related to the fact the orcid push at this moment is
        # triggered by the signal after_record_update (which happens after a
        # InspireRecord.commit()). This is not the actual commit to the db which
        # might happen at a later stage or not at all.
        # Note that connecting to the proper SQLAlchemy signal would also
        # have issues: https://github.com/mitsuhiko/flask-sqlalchemy/issues/645
        if self.record_db_version and inspire_record.model.version_id < self.record_db_version:
            raise exceptions.StaleRecordDBVersionException(
                'Requested push for db version={}, but actual record db'
                ' version={}'.format(self.record_db_version, inspire_record.model.version_id)
            )
        return inspire_record

    @property
    def _do_force_cache_miss(self):
        """
        Hook to force a cache miss. This can be leveraged in feature tests.
        """
        for note in self.inspire_record.get('_private_notes', []):
            if note.get('value') == 'orcid-push-force-cache-miss':
                logger.info('OrcidPusher force cache miss for recid={} and orcid={}'.format(
                    self.recid, self.orcid))
                return True
        return False

    @property
    def _is_record_deleted(self):
        # Hook to force a delete. This can be leveraged in feature tests.
        for note in self.inspire_record.get('_private_notes', []):
            if note.get('value') == 'orcid-push-force-delete':
                logger.info('OrcidPusher force delete for recid={} and orcid={}'.format(
                    self.recid, self.orcid))
                return True
        return self.inspire_record.get('deleted', False)

    @time_execution
    def push(self):
        putcode = None
        if not self._do_force_cache_miss:
            putcode = self.cache.read_work_putcode()
            if not self._is_record_deleted and \
                    not self.cache.has_work_content_changed(self.inspire_record):
                logger.info('OrcidPusher cache hit for recid={} and orcid={}'.format(
                    self.recid, self.orcid))
                return putcode
        logger.info('OrcidPusher cache miss for recid={} and orcid={}'.format(
            self.recid, self.orcid))

        # If the record is deleted, then delete it.
        if self._is_record_deleted:
            self._delete_work(putcode)
            return None

        self.converter = OrcidConverter(
            record=self.inspire_record,
            url_pattern=current_app.config['LEGACY_RECORD_URL_PATTERN'],
            put_code=putcode,
        )

        try:
            putcode = self._post_or_put_work(putcode)
        except orcid_client_exceptions.WorkAlreadyExistsException:
            # We POSTed the record as new work, but it failed because the work
            # already exists (identified by the external identifiers).
            # This means we do not have the putcode, thus we cache all
            # author's putcodes and PUT the work again.
            try:
                if self.do_fail_if_duplicated_identifier:
                    raise exceptions.DuplicatedExternalIdentifierPusherException
                self._push_work_with_clashing_identifier()
                self._post_or_put_work(putcode)
            except orcid_client_exceptions.WorkAlreadyExistsException:
                putcode = self._cache_all_author_putcodes()
                if not putcode:
                    msg = 'No putcode was found in ORCID API for orcid={} and recid={}.'\
                        ' And the POST has previously failed for the same recid because'\
                        ' the work had already existed'.format(self.orcid, self.recid)
                    raise exceptions.PutcodeNotFoundInOrcidException(msg)
                putcode = self._post_or_put_work(putcode)
        except orcid_client_exceptions.DuplicatedExternalIdentifierException:
            # We PUT a record changing its identifier, but there is another work
            # in ORCID with the same identifier. We need to find out the recid
            # of the clashing work in ORCID and push a fresh version of that
            # record.
            # This scenario might be triggered by a merge of 2 records in Inspire.
            if self.do_fail_if_duplicated_identifier:
                raise exceptions.DuplicatedExternalIdentifierPusherException
            self._push_work_with_clashing_identifier()
            putcode = self._post_or_put_work(putcode)
        except orcid_client_exceptions.PutcodeNotFoundPutException:
            self.cache.delete_work_putcode()
            putcode = self._post_or_put_work()
        except (orcid_client_exceptions.TokenInvalidException,
                orcid_client_exceptions.TokenMismatchException,
                orcid_client_exceptions.TokenWithWrongPermissionException):
            logger.info('Deleting Orcid push access token={} for orcid={}'.format(
                self.oauth_token, self.orcid))
            push_access_tokens.delete_access_token(self.oauth_token, self.orcid)
            raise exceptions.TokenInvalidDeletedException
        except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
            raise exceptions.InputDataInvalidException(from_exc=exc)

        self.cache.write_work_putcode(putcode, self.inspire_record)
        return putcode

    @time_execution
    def _post_or_put_work(self, putcode=None):
        # Note: if putcode is None, then it's a POST (it means the work is new).
        # Otherwise a PUT (it means the work already exists and it has the given
        # putcode).

        xml_element = self.converter.get_xml(do_add_bibtex_citation=True)
        # ORCID API allows 1 non-idempotent call only for the same orcid at
        # the same time. Using `distributed_lock` to achieve this.
        with distributed_lock(self.lock_name, blocking=True):
            if putcode:
                response = self.client.put_updated_work(xml_element, putcode)
            else:
                response = self.client.post_new_work(xml_element)

        utils.log_service_response(logger, response, 'in OrcidPusher for recid={}'.format(self.recid))
        response.raise_for_result()
        return response['putcode']

    @time_execution
    def _cache_all_author_putcodes(self):
        logger.info('New OrcidPusher cache all author putcodes for orcid={}'.format(self.orcid))
        putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)
        putcodes_recids = list(putcode_getter.get_all_inspire_putcodes_and_recids_iter())  # Can raise exceptions.InputDataInvalidException.

        putcode = None
        for fetched_putcode, fetched_recid in putcodes_recids:
            if fetched_recid == str(self.recid):
                putcode = int(fetched_putcode)
            cache = OrcidCache(self.orcid, fetched_recid)
            cache.write_work_putcode(fetched_putcode)

        # Ensure the putcode is actually in cache.
        # Note: this step is not really necessary and it can be skipped, but
        # at this moment it helps isolate a potential issue.
        if putcode and not self.cache.read_work_putcode():
            raise exceptions.PutcodeNotFoundInCacheAfterCachingAllPutcodes(
                'No putcode={} found in cache for recid={} after having'
                ' cached all author putcodes for orcid={}'.format(
                    self.putcode, self.recid, self.orcid))

        return putcode

    @time_execution
    def _delete_work(self, putcode=None):
        putcode = putcode or self._cache_all_author_putcodes()
        if not putcode:
            # Such recid does not exists (anymore?) in ORCID API.
            return

        # ORCID API allows 1 non-idempotent call only for the same orcid at
        # the same time. Using `distributed_lock` to achieve this.
        with distributed_lock(self.lock_name, blocking=True):
            response = self.client.delete_work(putcode)
        try:
            response.raise_for_result()
        except orcid_client_exceptions.PutcodeNotFoundDeleteException:
            # Such putcode does not exists (anymore?) in orcid.
            pass
        except orcid_client_exceptions.BaseOrcidClientJsonException as exc:
            raise exceptions.InputDataInvalidException(from_exc=exc)

        self.cache.delete_work_putcode()

    @time_execution
    def _push_work_with_clashing_identifier(self):
        putcode_getter = OrcidPutcodeGetter(self.orcid, self.oauth_token)

        ids = self.converter.added_external_identifiers
        for putcode, recid in putcode_getter.get_putcodes_and_recids_by_identifiers_iter(ids):
            if not putcode or not recid:
                continue
            # Local import to avoid import error.
            from inspirehep.modules.orcid import tasks
            max_retries = 3
            # Execute the orcid_push Celery task synchronously.
            backoff = lambda retry_count: [30, 2 * 60, 7 * 60][retry_count % max_retries]  # noqa: E731ß
            utils.apply_celery_task_with_retry(
                tasks.orcid_push,
                kwargs={
                    'orcid': self.orcid,
                    'rec_id': recid,
                    'oauth_token': self.oauth_token,
                    # Set `do_fail_if_duplicated_identifier` to avoid an
                    # infinite recursive calls chain.
                    'kwargs_to_pusher': dict(
                        do_fail_if_duplicated_identifier=True,
                        record_db_version=self.record_db_version)
                },
                max_retries=max_retries,
                countdown=backoff,
                time_limit=10 * 60,
            )
