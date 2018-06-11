#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Update legacy_records_mirror table"""

from __future__ import absolute_import, division, print_function

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9ea5752e7a5'
down_revision = '17ff155db70d'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        'legacy_records_mirror',
        sa.Column(
            'collection',
            sa.Text(),
            default='',
        )
    )


def downgrade():
    """Downgrade database."""
    op.drop_column(
        'legacy_records_mirror',
        'collection',
    )
