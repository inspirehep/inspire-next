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

"""Create inspirehep tables."""

from __future__ import absolute_import, division, print_function

from datetime import datetime
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fddb3cfe7a9c'
down_revision = 'a82a46d12408'
branch_labels = ()
# `a26f133d42a9` -> `invenio_workflows`
# `9848d0149abd` -> `invenio_accounts`
depends_on = 'a26f133d42a9', '9848d0149abd'


def upgrade():
    """Upgrade database."""
    op.create_table(
        'inspire_prod_records',
        sa.Column('recid', sa.Integer, primary_key=True, index=True),
        sa.Column(
            'last_updated',
            sa.DateTime,
            default=datetime.utcnow,
            nullable=False,
            index=True
        ),
        sa.Column('marcxml', sa.LargeBinary, nullable=False),
        sa.Column(
            'valid',
            sa.Boolean,
            default=None,
            nullable=True,
            index=True),
        sa.Column('errors', sa.Text(), nullable=True)
    )

    op.create_table(
        'workflows_audit_logging',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('last_updated', sa.DateTime, default=datetime.utcnow, nullable=False, index=True),
        sa.Column(
            'user_id',
            sa.Integer,
            sa.ForeignKey("accounts_user.id", ondelete='CASCADE'),
            nullable=True,
            index=True,
        ),
        sa.Column('score', sa.Float, default=0, nullable=False),
        sa.Column('user_action', sa.Text, default='', nullable=False),
        sa.Column('decision', sa.Text, default='', nullable=False),
        sa.Column('source', sa.Text, default='', nullable=False),
        sa.Column('action', sa.Text, default='', nullable=False)
    )

    op.create_table(
        'workflows_pending_record',
        sa.Column(
            'workflow_id',
            sa.Integer,
            sa.ForeignKey("workflows_object.id", ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column('record_id', sa.Integer, nullable=False)
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('inspire_prod_records')
    op.drop_table('workflows_audit_logging')
    op.drop_table('workflows_pending_record')
