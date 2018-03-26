# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from os.path import basename

from flask import json

from invenio_workflows_ui.serializers.json import JSONSerializer
from inspire_utils.record import get_value
from inspirehep.utils.record_getter import get_db_record


class WorkflowJSONSerializer(JSONSerializer):
    def serialize(self, workflow_ui_object):
        fuzzy_matches = get_value(workflow_ui_object, '_extra_data.matches.fuzzy')

        if fuzzy_matches is not None:
            workflow_ui_object['_extra_data']['matches']['fuzzy'] = \
                map(self._ref_to_literature_brief, fuzzy_matches)

        return json.dumps(workflow_ui_object.dumps(), **self._format_args())

    def _ref_to_literature_brief(self, record_ref):
        recid = basename(record_ref['$ref'])
        record = get_db_record('lit', recid)
        brief = {
            'control_number': record['control_number'],
            'title': get_value(record, 'titles[0].title'),
        }

        abstract = get_value(record, 'abstracts[0].value')
        if abstract:
            brief['abstract'] = abstract

        return brief
