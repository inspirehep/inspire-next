#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Index signature_block field"""

from __future__ import absolute_import, division, print_function

from alembic import op

# revision identifiers, used by Alembic.
revision = '47bc5e7e1a87'
down_revision = '17ff155db70d'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.execute('''
        create function signature_blocks(json jsonb) returns text[] as $$
        select array_agg(a->>'signature_block') as result from jsonb_array_elements(json->'authors') as a;$$
        language sql immutable
        ''')
    op.execute('create index ix_records_metadata_json_signature_blocks on records_metadata using gin (signature_blocks(json))')


def downgrade():
    """Downgrade database."""
    op.execute('drop index if exists ix_records_metadata_json_signature_blocks')
    op.execute('drop function if exists signature_blocks(json jsonb)')
