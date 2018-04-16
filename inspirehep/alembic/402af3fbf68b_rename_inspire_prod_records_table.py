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

"""Rename the ``inspire_prod_records`` table.

Note:

    Alembic does not handle correctly the PostgreSQL case in its
    ``rename_table`` operation, so we have to manually amend some
    additional database metadata. For more information, please see:
    http://petegraham.co.uk/rename-postgres-table-with-alembic/

"""

from __future__ import absolute_import, division, print_function

from alembic import op

revision = '402af3fbf68b'
down_revision = 'd99c7038006'
branch_labels = ()
depends_on = None


def upgrade():
    op.rename_table('inspire_prod_records', 'legacy_records_mirror')
    op.execute('ALTER SEQUENCE inspire_prod_records_recid_seq RENAME TO legacy_records_mirror_recid_seq')
    op.execute('ALTER INDEX pk_inspire_prod_records RENAME TO pk_legacy_records_mirror')
    op.execute('ALTER INDEX ix_inspire_prod_records_last_updated RENAME TO ix_legacy_records_mirror_last_updated')
    op.execute('ALTER INDEX ix_inspire_prod_records_recid RENAME TO ix_legacy_records_mirror_recid')
    op.execute('ALTER INDEX ix_inspire_prod_records_valid RENAME TO ix_legacy_records_mirror_valid')


def downgrade():
    op.rename_table('legacy_records_mirror', 'inspire_prod_records')
    op.execute('ALTER SEQUENCE legacy_records_mirror_recid_seq RENAME TO inspire_prod_records_recid_seq')
    op.execute('ALTER INDEX pk_legacy_records_mirror RENAME TO pk_inspire_prod_records')
    op.execute('ALTER INDEX ix_legacy_records_mirror_last_updated RENAME TO ix_inspire_prod_records_last_updated')
    op.execute('ALTER INDEX ix_legacy_records_mirror_recid RENAME TO ix_inspire_prod_records_recid')
    op.execute('ALTER INDEX ix_legacy_records_mirror_valid RENAME TO ix_inspire_prod_records_valid')
