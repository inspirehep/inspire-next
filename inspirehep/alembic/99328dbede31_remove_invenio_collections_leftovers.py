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

"""Remove invenio-collections leftovers"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99328dbede31'
down_revision = '2f5368ff6d20'
branch_labels = ()
depends_on = '97faa437d867'


def upgrade():
    """Upgrade database."""
    op.drop_index(op.f('ix_collection_name'), table_name='collection')
    op.drop_index('collection_rgt_idx', table_name='collection')
    op.drop_index('collection_lft_idx', table_name='collection')
    op.drop_index('collection_level_idx', table_name='collection')

    op.drop_table('collection')


def downgrade():
    """Downgrade database."""
    op.create_table(
        'collection',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('dbquery', sa.Text(), nullable=True),
        sa.Column('rgt', sa.Integer(), nullable=False),
        sa.Column('lft', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('tree_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['parent_id'], ['collection.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'collection_level_idx', 'collection', ['level'], unique=False
    )
    op.create_index('collection_lft_idx', 'collection', ['lft'], unique=False)
    op.create_index('collection_rgt_idx', 'collection', ['rgt'], unique=False)
    op.create_index(
        op.f('ix_collection_name'), 'collection', ['name'], unique=True
    )
