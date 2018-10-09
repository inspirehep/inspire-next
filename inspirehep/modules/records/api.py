# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

"""Inspire Records"""

from __future__ import absolute_import, division, print_function

from copy import deepcopy
from datetime import datetime
import uuid
import arrow
from elasticsearch.exceptions import NotFoundError
from flask import current_app
from fs.opener import fsopen
from six.moves.urllib.parse import urlparse, unquote
from invenio_records.api import RecordMetadata

from inspire_dojson.utils import get_recid_from_ref, strip_empty_values, absolute_url
from inspire_schemas.api import validate
from inspire_schemas.builders import LiteratureBuilder
from invenio_files_rest.models import Bucket
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record
from invenio_db import db
from sqlalchemy import Text, or_, not_, cast, type_coerce
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql.functions import GenericFunction

from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.pidstore.utils import get_pid_type_from_schema, get_endpoint_from_pid_type
from inspirehep.modules.records.utils import populate_earliest_date
from inspirehep.utils.record_getter import (
    RecordGetterError,
    get_es_record_by_uuid
)

MAX_UNIQUE_KEY_COUNT = 50000


class referenced_records(GenericFunction):
    type = ARRAY(Text)


class InspireRecord(Record):
    """Record class that fetches records from DataBase."""

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Override the default ``create``.

        To handle also the docmuments and figures retrieval.

        Note:

            Might create an extra revision in the record if it had to download
            any documents or figures.

        Keyword Args:

            id_(uuid): an optional uuid to assign to the created record object.
            files_src_records(List[InspireRecord]): if passed, it will try to
                get the files for the documents and figures from the first
                record in the list that has it in it's files iterator before
                downloading them, for example to merge existing
                records.
            skip_files(bool): if ``True`` it will skip the files retrieval
                described above. Note also that, if not passed, it will fall
                back to the value of the ``RECORDS_SKIP_FILES`` configuration
                variable.

        Examples:
            >>> record = {
            ...     '$schema': 'hep.json',
            ... }
            >>> record = InspireRecord.create(record)
            >>> record.commit()
        """
        files_src_records = kwargs.pop('files_src_records', [])
        skip_files = kwargs.pop(
            'skip_files', current_app.config.get('RECORDS_SKIP_FILES'))

        id_ = id_ or uuid.uuid4()
        data = strip_empty_values(data)

        with db.session.begin_nested():
            cls.mint(id_, data)
            record = super(InspireRecord, cls).create(data, id_=id_, **kwargs)

        if not skip_files:
            record.download_documents_and_figures(
                src_records=files_src_records,
            )

        return record

    @classmethod
    def create_or_update(cls, data, **kwargs):
        """Create or update a record.

        It will check if there is any record registered with the same
        ``control_number`` and ``pid_type``. If it's ``True``, it will update
        the current record, otherwise it will create a new one.

        Keyword Args:

            files_src_records(List[InspireRecord]): if passed, it will try to
                get the files for the documents and figures from the first
                record in the list that has it in it's files iterator before
                downloading them, for example to merge existing
                records.
            skip_files(bool): if ``True`` it will skip the files retrieval
                described above. Note also that, if not passed, it will fall
                back to the value of the ``RECORDS_SKIP_FILES`` configuration
                variable.

        Examples:
            >>> record = {
            ...     '$schema': 'hep.json',
            ... }
            >>> record = InspireRecord.create_or_update(record)
            >>> record.commit()
        """

        pid_type = get_pid_type_from_schema(data['$schema'])
        control_number = data.get('control_number')

        files_src_records = kwargs.pop('files_src_records', [])
        skip_files = kwargs.pop(
            'skip_files', current_app.config.get('RECORDS_SKIP_FILES'))

        try:
            pid = PersistentIdentifier.get(pid_type, control_number)
            record = super(InspireRecord, cls).get_record(pid.object_uuid)
            record.clear()
            record.update(data, skip_files=skip_files, **kwargs)

            if data.get('legacy_creation_date'):
                record.model.created = datetime.strptime(data['legacy_creation_date'], '%Y-%m-%d')

        except PIDDoesNotExistError:
            record = cls.create(data, skip_files=skip_files, **kwargs)

            if data.get('legacy_creation_date'):
                record.model.created = datetime.strptime(data['legacy_creation_date'], '%Y-%m-%d')

        if data.get('deleted'):
            new_recid = get_recid_from_ref(data.get('new_record'))
            if not new_recid:
                record.delete()

        if not skip_files:
            record.download_documents_and_figures(
                src_records=files_src_records,
            )
        return record

    def update(self, data, **kwargs):
        """Override the default ``update``.

        To handle also the docmuments and figures retrieval.

        Keyword Args:

            files_src_records(InspireRecord): if passed, it will try to get the
                files for the documents and figures from this record's files
                iterator before downloading them, for example to merge existing
                records.
            skip_files(bool): if ``True`` it will skip the files retrieval
                described above. Note also that, if not passed, it will fall
                back to the value of the ``RECORDS_SKIP_FILES`` configuration
                variable.
        """
        files_src_records = kwargs.pop('files_src_records', ())
        skip_files = kwargs.pop(
            'skip_files', current_app.config.get('RECORDS_SKIP_FILES'))

        super(InspireRecord, self).update(data, **kwargs)

        if not skip_files:
            self.download_documents_and_figures(
                src_records=files_src_records,
                only_new=True,
            )

    def merge(self, other):
        """Redirect pidstore of current record to the other InspireRecord.

        Args:

            other(InspireRecord): The record that self(record) is going to be
                redirected.
        """
        pids_deleted = PersistentIdentifier.query.filter(
            PersistentIdentifier.object_uuid == self.id
        ).all()
        pid_merged = PersistentIdentifier.query.filter(
            PersistentIdentifier.object_uuid == other.id
        ).one()
        with db.session.begin_nested():
            for pid in pids_deleted:
                pid.redirect(pid_merged)
                db.session.add(pid)

    def delete(self):
        """Mark as deleted all pidstores for a specific record."""

        pids = PersistentIdentifier.query.filter(
            PersistentIdentifier.object_uuid == self.id
        ).all()

        with db.session.begin_nested():
            for pid in pids:
                pid.delete()
                db.session.add(pid)

        self['deleted'] = True

    def _delete(self, *args, **kwargs):
        super(InspireRecord, self).delete(*args, **kwargs)

    def _create_bucket(self, location=None, storage_class=None):
        """Create file bucket for workflow object."""
        if location is None:
            location = current_app.config[
                'RECORDS_DEFAULT_FILE_LOCATION_NAME'
            ]
        if storage_class is None:
            storage_class = current_app.config[
                'RECORDS_DEFAULT_STORAGE_CLASS'
            ]

        bucket = Bucket.create(
            location=location,
            storage_class=storage_class
        )
        return bucket

    def validate(self):
        """Validate the record, also ensuring format compliance."""
        validate(self)

    @staticmethod
    def mint(id_, data):
        """Mint the record."""
        return inspire_recid_minter(id_, data)

    def add_document_or_figure(
        self,
        metadata,
        stream=None,
        is_document=True,
        file_name=None,
        key=None,
    ):
        """Add a document or figure to the record.

        Args:

            metadata(dict): metadata of the document or figure, see the schemas
                for more details, will be validated.
            stream(file like object): if passed, will extract the file contents
                from it.
            is_document(bool): if the given information is for a document,
                set to ```False``` for a figure.
            file_name(str): Name of the file, used as a basis of the key for
                the files store.
            key(str): if passed, will use this as the key for the files store
                and ignore ``file_name``, use it to overwrite existing keys.


        Returns:

            dict: metadata of the added document or figure.


        Raises:

            TypeError: if not ``file_name`` nor ``key`` are passed (one of
                them is required).
        """
        if not key and not file_name:
            raise TypeError(
                'No file_name and no key passed, at least one of them is '
                'needed.'
            )

        if not key:
            key = self._get_unique_files_key(base_file_name=file_name)

        if stream is not None:
            self.files[key] = stream

        builder = LiteratureBuilder(record=self.to_dict())
        metadata['key'] = key
        metadata['url'] = '/api/files/{bucket}/{key}'.format(
            bucket=self.files[key].bucket_id,
            key=key,
        )
        if is_document:
            builder.add_document(**metadata)
        else:
            builder.add_figure(**metadata)

        super(InspireRecord, self).update(builder.record)
        return metadata

    def _resolve_doc_or_fig_url(
        self,
        doc_or_fig_obj,
        src_records=(),
        only_new=False,
    ):
        """Resolves the given document url according to the current record.

        It will fill it up with the local url in case it's found in the given
        src_records.


        Returns:

            dict: with the medatada of the given ``doc_or_fig_obj`` updated as
                follows:
                * In the case it has to be downloaded: the url is set to
                  something that you can use fsopen on.
                * In the case it does not have to be downloaded: the url is
                  left intact pointing to the /api/files endpoint.

        Raises:
            Exception: if the url of the given ``doc_or_fig_obj`` is
                unresolvable.
        """
        doc_or_fig_obj = deepcopy(doc_or_fig_obj)
        key = doc_or_fig_obj['key']
        src_record_file = next(
            (
                rec.files[key].file.uri
                for rec in src_records
                if key in rec.files
            ),
            None,
        )

        def _should_take_from_src_records(
            self,
            key,
            src_record_file,
            only_new,
        ):
            should_take = False
            if (
                not only_new and
                src_record_file
            ):
                should_take = True

            elif (
                only_new and
                src_record_file and
                key not in self.files
            ):
                should_take = True

            return should_take

        def _already_there(self, only_new):
            return (
                only_new and
                key in self.files
            )

        def _is_internal_document(doc_or_fig_obj):
            return doc_or_fig_obj['url'].startswith('/api/files/')

        def _get_meaningful_exception(
            self,
            key,
            src_record_file,
            only_new,
            doc_or_fig_obj,
        ):
            exception = None
            if not src_record_file and key not in self.files:
                exception = Exception(
                    "Bad document %s, refers to an already downloaded "
                    "url, but none found in this record nor in the passed "
                    "src_records."
                    % doc_or_fig_obj
                )
            elif not only_new and not src_record_file:
                exception = Exception(
                    "Can't download %s, as no src_records were passed that "
                    "contained it, and only_new was set to False."
                    % doc_or_fig_obj
                )
            else:
                exception = Exception(
                    "Unexpected document resolution error for document %s"
                    % doc_or_fig_obj
                )

            return exception

        if not _is_internal_document(doc_or_fig_obj):
            return doc_or_fig_obj

        if _should_take_from_src_records(self, key, src_record_file, only_new):
            doc_or_fig_obj['url'] = src_record_file
            return doc_or_fig_obj

        if _already_there(self, only_new):
            return doc_or_fig_obj

        raise _get_meaningful_exception(
            self,
            key,
            src_record_file,
            only_new,
            doc_or_fig_obj,
        )

    def _download_to_docs_or_figs(
        self,
        document=None,
        figure=None,
        src_records=(),
        only_new=False,
    ):
        if not document and not figure:
            raise TypeError(
                'No document nor figure passed, at least one is needed.'
            )

        is_document = bool(document)
        doc_or_fig_obj = self._resolve_doc_or_fig_url(
            doc_or_fig_obj=document or figure,
            src_records=src_records,
            only_new=only_new,
        )
        if doc_or_fig_obj['url'].startswith('/api/files/'):
            return self.add_document_or_figure(
                metadata=doc_or_fig_obj,
                key=doc_or_fig_obj['key'],
                is_document=is_document,
            )

        key = doc_or_fig_obj['key']
        if key not in self.files:
            key = self._get_unique_files_key(base_file_name=key)

        url = doc_or_fig_obj['url']
        scheme = urlparse(url).scheme
        if scheme == 'file':
            url = unquote(url)

        stream = fsopen(url, mode='rb')
        return self.add_document_or_figure(
            metadata=doc_or_fig_obj,
            key=key,
            stream=stream,
            is_document=is_document,
        )

    def download_documents_and_figures(self, only_new=False, src_records=()):
        """Gets all the documents and figures of the record, and downloads them
        to the files property.

        If the record does not have a control number yet, this function will
        do nothing and it will be left to the caller the task of calling it
        again once the control number is set.

        When iterating through the documents and figures, the following
        happens:

        * if `url` field points to the files api:
            * and there's no `src_records`:
              * and `only_new` is `False`: it will throw an error, as that
                would be the case that the record was created from scratch
                with a document that was already downloaded from another
                record, but that record was not passed, so we can't get the
                file.

              * and `only_new` is `True`:
                  * if `key` exists in the current record files: it will do
                    nothing, as the file is already there.

                  * if `key` does not exist in the current record files: An
                    exception will be thrown, as the file can't be retrieved.

            * and there's a `src_records`:
              * and `only_new` is `False`:
                  * if `key` exists in the src_records files: it will download
                    the file from the local path derived from the src_records
                    files.

                  * if `key` does not exist in the src_records files: An
                    exception will be thrown, as the file can't be retrieved.

              * and `only_new` is `True`:
                  * if `key` exists in the current record files: it will do
                    nothing, as the file is already there.

                  * if `key` does not exist in the current record files:
                    * if `key` exists in the src_records files: it will download
                      the file from the local path derived from the src_records
                      files.

                    * if `key` does not exist in the src_records files: An
                      exception will be thrown, as the file can't be retrieved.

        * if `url` field does not point to the files api: it will try to
          download the new file.

        Args:
            only_new(bool): If True, will not re-download any files if the
                document['key'] matches an existing downloaded file.
            src_records(List[InspireRecord]): if passed, it will try to get the
                files from this record files iterator before downloading them,
                for example to merge existing records.
        """
        if 'control_number' not in self:
            return

        documents_to_download = self.pop('documents', [])
        figures_to_download = self.pop('figures', [])

        for document in documents_to_download:
            self._download_to_docs_or_figs(
                document=document,
                src_records=src_records,
                only_new=only_new,
            )

        for figure in figures_to_download:
            self._download_to_docs_or_figs(
                figure=figure,
                src_records=src_records,
                only_new=only_new,
            )

    def _get_unique_files_key(self, base_file_name):
        def _strip_old_control_number(base_name):
            base_name = base_name.split('_', 1)[-1]
            return base_name

        def _append_current_control_number(control_number, base_name):
            prefix = '%s_' % control_number
            if not base_name.startswith(prefix):
                base_name = _strip_old_control_number(base_name)
                prepended_key = '%s%s' % (prefix, base_name)
            else:
                prepended_key = base_name

            return prepended_key

        prepended_key = _append_current_control_number(
            self['control_number'],
            base_file_name,
        )

        new_key = prepended_key
        count = 1
        while new_key in self.files:
            new_key = '%s_%s' % (prepended_key, count)
            count += 1
            # This should never happen, but just in case to abort infinite
            # loops we add this safeguard.
            if count > MAX_UNIQUE_KEY_COUNT:
                raise Exception(
                    'Unable to find a unique key in the first %s, aborting.'
                    % MAX_UNIQUE_KEY_COUNT
                )

        return new_key

    def _get_ref(self):
        """Returns full url to this object (as in $ref)"""
        pid_value = self.get('control_number')
        pid_type = get_pid_type_from_schema(self.get('$schema'))
        endpoint = get_endpoint_from_pid_type(pid_type)
        return absolute_url(u'/api/{endpoint}/{control_number}'.format(endpoint=endpoint,
                                                                       control_number=pid_value))

    def _query_citing_records(self, show_duplicates=False, session=None):
        """Returns records which cites this one."""
        if not session:
            session = db.session
        ref = self._get_ref()
        if not ref:
            raise Exception("There is no $ref for this object")
        citation_query = session.query(RecordMetadata).with_entities(RecordMetadata.id,
                                                                     RecordMetadata.json['control_number'])
        citation_filter = referenced_records(RecordMetadata.json).contains([ref])
        filter_deleted_records = or_(not_(type_coerce(RecordMetadata.json, JSONB).has_key('deleted')),  # noqa: W601
                                     not_(RecordMetadata.json['deleted'] == cast(True, JSONB)))
        only_literature_collection = type_coerce(RecordMetadata.json, JSONB)['_collections'].contains(['Literature'])
        citations = citation_query.filter(citation_filter,
                                          filter_deleted_records,
                                          only_literature_collection)
        if not show_duplicates:
            # It just hides duplicates, and still can show citations
            # which do not have proper PID in PID store
            # Duplicated data should be removed with the CLI command
            citations = citations.distinct(RecordMetadata.json['control_number'])
        return citations

    @property
    def get_citing_records_query(self):
        return self._query_citing_records()

    def get_citations_count(self, session=None, show_duplicates=False):
        """Returns citations count for this record."""

        count = self._query_citing_records(show_duplicates, session).count()
        return count

    def dumps(self):
        """Returns a dict 'representation' of the record.

        Note: this is not suitable to create a new record from it, as the
              representation will include some extra fields that should not be
              present in the record's json, see the 'to_dict' method instead.
        """
        base_dict = super(InspireRecord, self).dumps()
        populate_earliest_date(base_dict)
        return base_dict

    def to_dict(self):
        """Gets a deep copy of the record's json."""
        return deepcopy(dict(self))


class ESRecord(InspireRecord):
    """Record class that fetches records from ElasticSearch."""

    @classmethod
    def get_record(cls, object_uuid, with_deleted=False):
        """Get record instance from ElasticSearch."""
        try:
            return cls(get_es_record_by_uuid(object_uuid))
        except RecordGetterError as e:
            if isinstance(e.cause, NotFoundError):
                # Raise this error so the interface will render a 404 page
                # rather than a 500
                raise PIDDoesNotExistError('es_record', object_uuid)
            else:
                raise

    @property
    def updated(self):
        """Get last updated timestamp."""
        if self.get('_updated'):
            return arrow.get(self['_updated']).naive
        else:
            return datetime.utcnow()
