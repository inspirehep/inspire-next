#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Update workflows_record_sources table"""

from __future__ import absolute_import, division, print_function

import enum
import sqlalchemy as sa

from alembic import op
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '17ff155db70d'
down_revision = '402af3fbf68b'
branch_labels = ()
depends_on = None


class SourceEnum(enum.IntEnum):
    arxiv = 1
    submitter = 2
    publisher = 3


def upgrade():
    """Upgrade database."""
    op.add_column(
        'workflows_record_sources',
        sa.Column(
            'created',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=False,
        )
    )

    op.add_column(
        'workflows_record_sources',
        sa.Column(
            'updated',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=False,
        )
    )

    op.alter_column(
        'workflows_record_sources',
        'record_id',
        new_column_name='record_uuid',
    )

    op.alter_column(
        'workflows_record_sources',
        'source',
        existing_type=sa.Text,
        type_=sa.Enum(SourceEnum),
        postgresql_using='source::sourceenum',
    )

    op.alter_column(
        'workflows_record_sources',
        'json',
        type_=sa.dialects.postgresql.JSONB,
        postgresql_using='json::text::jsonb',
    )


def downgrade():
    """Downgrade database."""
    op.drop_column(
        'workflows_record_sources',
        'created',
    )

    op.drop_column(
        'workflows_record_sources',
        'updated',
    )

    op.alter_column(
        'workflows_record_sources',
        'record_uuid',
        new_column_name='record_id',
    )

    op.alter_column(
        'workflows_record_sources',
        'source',
        existing_type=sa.Enum(SourceEnum),
        type_=sa.Text,
        postgresql_using='source::text',
    )

    op.alter_column(
        'workflows_record_sources',
        'json',
        type_=sa.dialects.postgresql.JSON,
        postgresql_using='json::text::json',
    )
