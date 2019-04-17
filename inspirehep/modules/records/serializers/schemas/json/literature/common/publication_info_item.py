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


class PublicationInfoItemSchemaV1(Schema):
    artid = fields.Raw()
    journal_issue = fields.Raw()
    journal_title = fields.Raw()
    journal_volume = fields.Raw()
    material = fields.Raw()
    page_start = fields.Raw()
    page_end = fields.Raw()
    pubinfo_freetext = fields.Raw()
    year = fields.Raw()

    @pre_dump
    def empty_if_display_display_fields_missing(self, data):
        journal_title = data.get('journal_title')
        pubinfo_freetext = data.get('pubinfo_freetext')
        conference_record = data.get('conference_record')
        if (journal_title is None and pubinfo_freetext is None) or conference_record is not None:
            return {}
        return data
