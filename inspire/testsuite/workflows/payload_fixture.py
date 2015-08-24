# -*- coding: utf-8 -*-
# This file is part of INSPIRE.
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

"""Implements a workflow for testing."""


from invenio_oaiharvester.tasks.records import convert_record_to_json

from invenio.modules.deposit.models import DepositionType
from invenio.modules.workflows.tasks.marcxml_tasks import convert_record

from inspire.modules.workflows.models import create_payload


class payload_fixture(DepositionType):

    """A test workflow for the Payload class."""

    workflow = [
        # First we perform conversion from OAI-PMH XML to MARCXML
        convert_record("oaiarXiv2inspire_nofilter.xsl"),

        # Then we convert from MARCXML to SmartJSON object
        # TODO: Use DOJSON when we are ready to switch from bibfield
        convert_record_to_json,
        create_payload,
    ]
