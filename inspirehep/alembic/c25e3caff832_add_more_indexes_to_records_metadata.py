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

"""Add more indexes to the records_metadata table.

Note:

    This migration was already run manually in the PROD environment, so this
    only needs to be stamped, not applied, at deploy time.  It's not possible
    to use the ``CONCURRENTLY`` keyword here because the migration happens
    inside of a transaction, which disallows it.

"""

from __future__ import absolute_import, division, print_function

from alembic import op

revision = 'c25e3caff832'
down_revision = '402af3fbf68b'
branch_labels = ()
depends_on = None


def upgrade():
    op.execute("CREATE INDEX json_ids_index ON records_metadata USING gin ((json -> 'ids'))")
    op.execute("CREATE INDEX json_export_to_index ON records_metadata USING gin ((json -> '_export_to'))")


def downgrade():
    op.execute('DROP INDEX IF EXISTS json_ids_index')
    op.execute('DROP INDEX IF EXISTS json_export_to_index')
