#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""create index on referenced_records"""
from __future__ import absolute_import, division, print_function

from alembic import op

# revision identifiers, used by Alembic.
revision = '0bc0a6ee1bc0'
down_revision = '2f5368ff6d20'
branch_labels = ()
depends_on = '07fb52561c5c'


def upgrade():
    """Upgrade database."""
    op.execute('''
        create or replace function referenced_records(json jsonb) returns text[] as  $$
        select
            array_agg(
                references_arr->'record'->>'$ref'
            )  as result
         from
            jsonb_array_elements(json->'references') as references_arr; $$
        language sql immutable
    ''')
    op.execute('''
        create index ix_records_metadata_json_referenced_records
            on records_metadata
            using gin(referenced_records(json))
    ''')


def downgrade():
    """Downgrade database."""
    op.execute('drop index if exists ix_records_metadata_json_referenced_records')
    op.execute('drop function if exists referenced_records(json jsonb)')
