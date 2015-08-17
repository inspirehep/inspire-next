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
    return "Checks the BibWorkflowObject's extra data for instance keys," \
           "and replaces them with their ids."


def do_upgrade():
    """Implement your upgrades here."""
    from flask import current_app
    from invenio.modules.workflows.models import BibWorkflowObject
    from invenio.modules.classifier.tasks.classification import check_for_objects_in_data

    all_objects = BibWorkflowObject.query.all()
    current_app.logger.info("Applying changes on objects ({0} records)".format(
        len(all_objects)
    ))
    for obj in all_objects:
        try:
            extra_data = obj.get_extra_data()
            result = extra_data['_tasks_results']['classification'][0]['result']
            check_for_objects_in_data(result)

            obj.set_extra_data(extra_data)
            obj.save()
        except KeyError:
            pass

    current_app.logger.info("Upgrade ended.")


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    pass


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    pass