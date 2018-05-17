#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Update workflows_record_sources table"""

from __future__ import absolute_import, division, print_function

import sqlalchemy as sa

from alembic import op
from datetime import datetime
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '17ff155db70d'
down_revision = '402af3fbf68b'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    source_enum = postgresql.ENUM('arxiv', 'submitter', 'publisher', name='source_enum')
    source_enum.create(op.get_bind())

    op.add_column(
        'workflows_record_sources',
        sa.Column(
            'created',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=True,
        )
    )

    op.add_column(
        'workflows_record_sources',
        sa.Column(
            'updated',
            sa.DateTime(),
            default=datetime.utcnow,
            nullable=True,
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
        type_=sa.Enum('arxiv', 'submitter', 'publisher', name='source_enum'),
        postgresql_using='source::source_enum',
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
        existing_type=sa.Enum('arxiv', 'submitter', 'publisher', name='source_enum'),
        type_=sa.Text,
        postgresql_using='source::text',
    )

    op.alter_column(
        'workflows_record_sources',
        'json',
        type_=sa.dialects.postgresql.JSON,
        postgresql_using='json::text::json',
    )

    source_enum = postgresql.ENUM('arxiv', 'submitter', 'publisher', name='source_enum')
    source_enum.drop(op.get_bind())
