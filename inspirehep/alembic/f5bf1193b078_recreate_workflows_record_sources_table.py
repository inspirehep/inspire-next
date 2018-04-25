#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Recreate workflows_record_sources_table"""

from __future__ import absolute_import, division, print_function

import enum
import sqlalchemy as sa

from alembic import op
from datetime import datetime
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils.types import JSONType, UUIDType

revision = 'f5bf1193b078'
down_revision = 'cb5153afd839'
branch_labels = ()
depends_on = None


class SourceEnum(enum.IntEnum):
    arxiv = 1
    submitter = 2
    publisher = 3


def upgrade():
    """Upgrade database."""
    op.drop_table('workflows_record_sources')
    op.create_table(
        'workflows_record_sources',
        sa.Column(
            'record_id',
            UUIDType,
            sa.ForeignKey('records_metadata.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'source',
            sa.Enum(SourceEnum),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('record_id', 'source'),
        sa.Column(
            'created',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=False
        ),
        sa.Column(
            'updated',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=False
        ),
        sa.Column(
            'json',
            postgresql.JSONB(),
            default=lambda: dict(),
            nullable=True
        ),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('workflows_record_sources')
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
