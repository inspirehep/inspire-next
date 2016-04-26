# -*- coding: utf-8 -*-
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Receivers for INSPIRE workflows."""

import six

from dojson.contrib.marc21.utils import create_record
from invenio_oaiharvester.signals import oaiharvest_finished

from inspirehep.dojson.hep import hep
from inspirehep.modules.converter.xslt import convert


# FIXME: This is only temporary until hepcrawl integration
@oaiharvest_finished.connect
def spawn_arXiv_workflow_from_oai_harvest(request, records, name, **kwargs):
    """Receive a list of harvested arXiv records and schedule workflow."""
    from flask import current_app
    from invenio_workflows import start, workflows

    if not request.endpoint == "http://export.arxiv.org/oai2":
        return

    workflow = "arxiv_ingestion"

    if workflow not in workflows:
        current_app.logger.warning(
            "{0} not in available workflows. Skipping workflow {1}.".format(
                workflow, name
            )
        )
        return

    for record in records:
        recxml = six.text_type(record)
        marcxml = convert(recxml, "oaiarXiv2marcxml.xsl")
        record = create_record(marcxml)
        hep_record = hep.do(record)
        start.delay(workflow, data=[hep_record])
