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

"""Fix the production DB."""

from __future__ import absolute_import, division, print_function

from alembic import op

revision = '53e8594bc789'
down_revision = 'd99c70308006'
branch_labels = ()
depends_on = None


PRIMARY_KEYS_MAP = {
    'access_actionsroles': dict(old='access_actionsroles_pkey', new='pk_access_actionsroles'),
    'access_actionsusers': dict(old='access_actionsusers_pkey', new='pk_access_actionsusers'),
    'accounts_role': dict(old='accounts_role_pkey', new='pk_accounts_role'),
    'accounts_user': dict(old='accounts_user_pkey', new='pk_accounts_user'),
    'accounts_user_session_activity': dict(old='accounts_user_session_activity_pkey', new='pk_accounts_user_session_activity'),
    'collection': dict(old='collection_pkey', new='pk_collection'),
    'crawler_job': dict(old='crawler_job_pkey', new='pk_crawler_job'),
    'crawler_workflows_object': dict(old='crawler_workflows_object_pkey', new='pk_crawler_workflows_object'),
    'files_bucket': dict(old='files_bucket_pkey', new='pk_files_bucket'),
    'files_buckettags': dict(old='files_buckettags_pkey', new='pk_files_buckettags'),
    'files_files': dict(old='files_files_pkey', new='pk_files_files'),
    'files_location': dict(old='files_location_pkey', new='pk_files_location'),
    'files_multipartobject': dict(old='files_multipartobject_pkey', new='pk_files_multipartobject'),
    'files_multipartobject_part': dict(old='files_multipartobject_part_pkey', new='pk_files_multipartobject_part'),
    'files_object': dict(old='files_object_pkey', new='pk_files_object'),
    'inspire_prod_records': dict(old='inspire_prod_records_pkey', new='pk_inspire_prod_records'),
    'oaiharvester_configs': dict(old='oaiharvester_configs_pkey', new='pk_oaiharvester_configs'),
    'oauthclient_remoteaccount': dict(old='oauthclient_remoteaccount_pkey', new='pk_oauthclient_remoteaccount'),
    'oauthclient_remotetoken': dict(old='oauthclient_remotetoken_pkey', new='pk_oauthclient_remotetoken'),
    'oauthclient_useridentity': dict(old='oauthclient_useridentity_pkey', new='pk_oauthclient_useridentity'),
    'pidstore_pid': dict(old='pidstore_pid_pkey', new='pk_pidstore_pid'),
    'pidstore_recid': dict(old='pidstore_recid_pkey', new='pk_pidstore_recid'),
    'pidstore_redirect': dict(old='pidstore_redirect_pkey', new='pk_pidstore_redirect'),
    'records_buckets': dict(old='records_buckets_pkey', new='pk_records_buckets'),
    'records_metadata': dict(old='records_metadata_pkey', new='pk_records_metadata'),
    'records_metadata_version': dict(old='records_metadata_version_pkey', new='pk_records_metadata_version'),
    'transaction': dict(old='transaction_pkey', new='pk_transaction'),
    'userprofiles_userprofile': dict(old='userprofiles_userprofile_pkey', new='pk_userprofiles_userprofile'),
    'workflows_audit_logging': dict(old='workflows_audit_logging_pkey', new='pk_workflows_audit_logging'),
    'workflows_buckets': dict(old='workflows_buckets_pkey', new='pk_workflows_buckets'),
    'workflows_object': dict(old='workflows_object_pkey', new='pk_workflows_object'),
    'workflows_pending_record': dict(old='workflows_pending_record_pkey', new='pk_workflows_pending_record'),
    'workflows_workflow': dict(old='workflows_workflow_pkey', new='pk_workflows_workflow'),
}

INDEXES_MAP = {
    'records_metadata': [
        dict(old='idxgindoctype', new='ix_records_metadata_json_document_type'),
        dict(old='idxgintitles', new='ix_records_metadata_json_titles'),
        dict(old='idxginjournaltitle', new='ix_records_metadata_json_journal_title'),  # journal_title gin.
        dict(old='idxgincollections', new='ix_records_metadata_json__collections2'),
        dict(old='json_ids_index', new='ix_records_metadata_json_ids'),
        dict(old='json_export_to_index', new='ix_records_metadata_json__export_to'),
        dict(old='_collections', new='ix_records_metadata_json__collections'),
        dict(old='journal_title', new='ix_records_metadata_json_journal_title2'),  # journal_title btree.
    ]
}


def upgrade():
    # Rename primary keys.
    for _, names in PRIMARY_KEYS_MAP.items():
        op.execute('ALTER INDEX IF EXISTS {} RENAME TO {}'.format(names['old'], names['new']))

    # Create indexes.
    # Notes:
    # - PostgreSQL 9.4.5 running in PROD on 2018.04.25 does *NOT* support the "IF NOT EXISTS" in "CREATE INDEX IF NOT EXISTS".
    # - PostgreSQL 9.6.2 running in QA on 2018.04.25 does support the "IF NOT EXISTS" in "CREATE INDEX IF NOT EXISTS".
    # The simplest way to implement a "CREATE INDEX IF NOT EXISTS" compatible with old and new versions of PostgreSQL
    # is to first delete the index is exists.
    op.execute("DROP INDEX IF EXISTS json_ids_index")
    op.execute("DROP INDEX IF EXISTS json_export_to_index")
    op.execute("DROP INDEX IF EXISTS _collections")
    op.execute("DROP INDEX IF EXISTS journal_title")

    op.execute("CREATE INDEX json_ids_index ON records_metadata USING gin ((json -> 'ids'))")
    op.execute("CREATE INDEX json_export_to_index ON records_metadata USING gin ((json -> '_export_to'))")
    op.execute("CREATE INDEX _collections ON records_metadata USING btree ((json ->> '_collections'::text) COLLATE pg_catalog.\"default\")")
    op.execute("CREATE INDEX journal_title ON records_metadata USING btree ((json ->> 'journal_title'::text) COLLATE pg_catalog.\"default\")")

    # Rename indexes.
    for _, names_list in INDEXES_MAP.items():
        for names in names_list:
            op.execute('ALTER INDEX {} RENAME TO {}'.format(names['old'], names['new']))


def downgrade():
    # Rename primary keys.
    for _, names in PRIMARY_KEYS_MAP.items():
        op.execute('ALTER INDEX {} RENAME TO {}'.format(names['new'], names['old']))

    # Rename indexes.
    for _, names_list in INDEXES_MAP.items():
        for names in names_list:
            op.execute('ALTER INDEX IF EXISTS {} RENAME TO {}'.format(names['new'], names['old']))
