# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


depends_on = []


def info():
    return "Updates all objects to run new task."


def do_upgrade():
    """Implement your upgrades here."""
    from flask import current_app
    from invenio_workflows.models import BibWorkflowObject
    from inspire.modules.workflows.tasks.matching import arxiv_set_category_field

    all_objects = BibWorkflowObject.query.filter(
        BibWorkflowObject.data_type == "arXiv"
    ).all()
    current_app.logger.info("Starting conversion of objects ({0} records)".format(
        len(all_objects)
    ))
    for obj in all_objects:
        obj.data = obj.get_data()
        if obj.data and not isinstance(obj.data, str):
            arxiv_set_category_field(obj, None)
            obj.save()

    current_app.logger.info("Conversion ended")


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    pass


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    pass
