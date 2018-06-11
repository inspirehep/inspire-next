#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Insert migrator-use-api action into access_actionsroles table"""

from __future__ import absolute_import, division, print_function

from alembic import op
from sqlalchemy.orm import sessionmaker
from invenio_access.models import ActionRoles
from invenio_accounts.models import Role

# revision identifiers, used by Alembic.
revision = 'eaab22c59b89'
down_revision = 'f9ea5752e7a5'
branch_labels = ()
depends_on = None
Session = sessionmaker()


def upgrade():
    """Upgrade database."""
    bind = op.get_bind()
    session = Session(bind=bind)

    cataloger = session.query(Role).filter(Role.name == 'cataloger').one()
    session.add(ActionRoles(
        action='migrator-use-api',
        role=cataloger)
    )

    session.commit()


def downgrade():
    """Downgrade database."""
    bind = op.get_bind()
    session = Session(bind=bind)

    session.query(ActionRoles).filter(ActionRoles.action == 'migrator-use-api').delete()

    session.commit()
