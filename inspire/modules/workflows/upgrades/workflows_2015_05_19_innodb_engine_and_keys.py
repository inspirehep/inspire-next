# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

from invenio_upgrader.api import op
from invenio.ext.sqlalchemy import db
from invenio.utils.text import wait_for_user


depends_on = [u'workflows_2014_08_12_initial']


def info():
    return "Upgrades workflows tables to InnoDB and adds some indexes"


def do_upgrade():
    """Implement your upgrades here."""
    # First upgrade bwlWORKFLOW for proper foreign key creation
    with op.batch_alter_table("bwlWORKFLOW", recreate="always", table_kwargs={"mysql_engine": 'InnoDB'}) as batch_op:
        pass

    with op.batch_alter_table("bwlOBJECT", recreate="always", table_kwargs={"mysql_engine": 'InnoDB'}) as batch_op:
        batch_op.create_index('ix_bwlOBJECT_version', ['version'])
        batch_op.create_index('ix_bwlOBJECT_data_type', ['data_type'])
        batch_op.create_foreign_key("bwlOBJECT_ibfk_1",
                                    "bwlWORKFLOW",
                                    ["id_workflow"],
                                    ["uuid"],
                                    ondelete="CASCADE")

    op.create_foreign_key("bwlOBJECT_ibfk_2",
                          "bwlOBJECT",
                          "bwlOBJECT",
                          ["id_parent"],
                          ["id"],
                          ondelete="CASCADE")

    with op.batch_alter_table("bwlWORKFLOWLOGGING", recreate="always", table_kwargs={"mysql_engine": 'InnoDB'}) as batch_op:
        batch_op.create_foreign_key("bwlWORKFLOWLOGGING_ibfk_1",
                                    "bwlWORKFLOW",
                                    ["id_object"],
                                    ["uuid"])

    with op.batch_alter_table("bwlOBJECTLOGGING", recreate="always", table_kwargs={"mysql_engine": 'InnoDB'}) as batch_op:
        batch_op.create_foreign_key("bwlOBJECTLOGGING_ibfk_1",
                                    "bwlOBJECT",
                                    ["id_object"],
                                    ["id"])

def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Check for potentially invalid revisions"""

    # Check for any inconsistent data
    missing_parents = list(db.engine.execute(
        """SELECT id, id_parent FROM bwlOBJECT WHERE id_parent NOT IN (SELECT id FROM bwlOBJECT)"""
    ))
    if missing_parents:
        warnings.warn("Inconsistent parent IDs in bwlOBJECT '{0}'".format(
            missing_parents
        ))
        try:
            wait_for_user("\nSetting all dangling parents to NULL? (Ctrl+C to stop)\n")
        except SystemExit:
            raise RuntimeError("Upgrade aborted by user.")
        for parent in missing_parents:
            db.engine.execute(
                """UPDATE bwlOBJECT SET id_parent=NULL WHERE id={0}""".format(parent[0])
            )

    dangling_logs = list(db.engine.execute(
        """SELECT id_object FROM bwlOBJECTLOGGING WHERE id_object NOT IN (SELECT id FROM bwlOBJECT)"""
    )) + list(db.engine.execute(
        """SELECT id_object FROM bwlWORKFLOWLOGGING WHERE id_object NOT IN (SELECT uuid FROM bwlWORKFLOW)"""
    ))
    if dangling_logs:
        warnings.warn("Inconsistent logs in bwlOBJECT/bwlWORKFLOW '{0}'".format(
            len(dangling_logs)
        ))
        try:
            wait_for_user("\nDelete all dangling logs? (Ctrl+C to stop)\n")
        except SystemExit:
            raise RuntimeError("Upgrade aborted by user.")
        db.engine.execute(
            """DELETE FROM bwlOBJECTLOGGING WHERE id_object NOT IN (SELECT id FROM bwlOBJECT)"""
        )
        db.engine.execute(
            """DELETE FROM bwlWORKFLOWLOGGING WHERE id_object NOT IN (SELECT uuid FROM bwlWORKFLOW)"""
        )

def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
