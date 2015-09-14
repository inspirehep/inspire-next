# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


depends_on = []


def info():
    return "Renames the inspire_approval action to approval."


def do_upgrade():
    """Implement your upgrades here."""
    from flask import current_app
    from invenio_workflows.models import BibWorkflowObject
    all_objects = BibWorkflowObject.query.all()
    count = 0
    current_app.logger.info("Starting conversion of actions ({0} records)".format(
        len(all_objects)
    ))
    for obj in all_objects:
        action = obj.get_action()
        if action and action == "inspire_approval":
            obj.set_action("core_approval", obj.get_action_message())
            obj.save()
            count += 1
    current_app.logger.info("Conversion ended ({0}/{1} records)".format(
        count,
        len(all_objects)
    ))


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    pass


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    pass
