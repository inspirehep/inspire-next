# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import warnings

from sqlalchemy.exc import OperationalError

from invenio_ext.sqlalchemy import db
from invenio_upgrader.api import op

# Important: Below is only a best guess. You MUST validate which previous
# upgrade you depend on.
depends_on = [u'inspire_2015_11_24_prod_records']


def info():
    """Info message."""
    return "Add new columns to inspire_prod_records tables"


def do_upgrade():
    """Implement your upgrades here."""
    try:
        op.add_column('inspire_prod_records',
                      db.Column('valid',
                                db.Boolean,
                                default=None,
                                nullable=True,
                                index=True)
                      )
        op.add_column('inspire_prod_records',
                      db.Column('errors',
                                db.Text(),
                                nullable=True)
                      )
    except OperationalError as err:
        # Columns exist
        warnings.warn(
            "*** Error adding columns 'inspire_prod_records.valid' "
            "and 'inspire_prod_records.errors': {0} ***".format(
                str(err)
            )
        )


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    # Example of raising errors:
    # raise RuntimeError("Description of error 1", "Description of error 2")


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
