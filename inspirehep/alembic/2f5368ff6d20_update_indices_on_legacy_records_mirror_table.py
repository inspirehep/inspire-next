#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add index on legacy_records_mirror"""

from __future__ import absolute_import, division, print_function

from alembic import op


# revision identifiers, used by Alembic.
revision = '2f5368ff6d20'
down_revision = 'eaab22c59b89'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_index(
        'ix_legacy_records_mirror_valid_collection',
        'legacy_records_mirror',
        ['valid', 'collection'],
    )

    op.drop_index(
        'ix_legacy_records_mirror_valid',
        'legacy_records_mirror',
    )

    op.drop_index(
        'ix_legacy_records_mirror_recid',
        'legacy_records_mirror',
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        'ix_legacy_records_mirror_valid_collection',
        'legacy_records_mirror',
    )

    op.create_index(
        'ix_legacy_records_mirror_valid',
        'legacy_records_mirror',
        ['valid'],
    )

    op.create_index(
        'ix_legacy_records_mirror_recid',
        'legacy_records_mirror',
        ['recid'],
    )
