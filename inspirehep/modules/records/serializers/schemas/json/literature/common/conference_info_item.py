# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from marshmallow import Schema, pre_dump, fields

from inspirehep.modules.records.utils import get_pid_from_record_uri
from inspirehep.utils.record_getter import get_db_record, RecordGetterError


class ConferenceInfoItemSchemaV1(Schema):
    titles = fields.Raw()
    control_number = fields.Raw()
    page_start = fields.Raw()
    page_end = fields.Raw()
    acronyms = fields.Raw()

    @pre_dump
    def resolve_conference_record_as_root(self, pub_info_item):
        conference_record = pub_info_item.get('conference_record')
        if conference_record is None:
            return {}

        _, recid = get_pid_from_record_uri(conference_record.get('$ref'))
        try:
            conference = get_db_record('con', recid)
        except RecordGetterError:
            return {}

        titles = conference.get('titles')
        if titles is None:
            return {}
        pub_info_item.update(conference)
        return conference.to_dict()
