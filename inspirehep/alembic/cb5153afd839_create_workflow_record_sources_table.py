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

"""Create the ``workflow_record_sources`` table."""

from __future__ import absolute_import, division, print_function

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.types import JSONType, UUIDType


revision = 'cb5153afd839'
down_revision = 'fddb3cfe7a9c'
branch_labels = ()
depends_on = '862037093962'


def upgrade():
    """Upgrade database."""
    op.create_table(
        'workflows_record_sources',
        sa.Column(
            'source',
            sa.Text,
            default='',
            nullable=False,
        ),
        sa.Column(
            'record_id',
            UUIDType,
            sa.ForeignKey('records_metadata.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('record_id', 'source'),
        sa.Column(
            'json',
            JSONType().with_variant(
                postgresql.JSON(none_as_null=True),
                'postgresql',
            ),
            default=lambda: dict(),
        ),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('workflows_record_sources')
