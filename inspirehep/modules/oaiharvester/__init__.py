# -*- coding: utf-8; -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""OAI harvester signal receivers."""

import six

from invenio_oaiharvester.signals import oaiharvest_finished


@oaiharvest_finished.connect
def spawn_workflow_from_oai_harvest(request, records, name, **kwargs):
    """Receive a list of harvested OAI-PMH records and schedule workflow."""
    from flask import current_app
    from invenio_workflows.api import start_delayed
    from invenio_workflows.registry import workflows

    workflow = current_app.config.get('OAIHARVESTER_WORKFLOWS', {}).get(name)
    if not workflow:
        return

    if workflow not in workflows:
        current_app.logger.warning(
            "{0} not in available workflows. Skipping OAI-PMH workflow {1}.".format(
                workflow, name
            )
        )
        return

    for record in records:
        recxml = six.text_type(record)
        start_delayed(workflow, data=[recxml])
