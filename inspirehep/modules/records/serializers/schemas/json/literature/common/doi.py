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

from marshmallow import Schema, post_dump, fields


class DOISchemaV1(Schema):
    material = fields.Raw()
    value = fields.Raw()

    @post_dump(pass_many=True)
    def filter(self, data, many):
        if many:
            return self.remove_duplicate_doi_values(data)
        return data

    @staticmethod
    def remove_duplicate_doi_values(dois):
        taken_doi_values = set()
        unique_dois = []
        for doi in dois:
            doi_value = doi.get('value')
            if doi_value not in taken_doi_values:
                taken_doi_values.add(doi_value)
                unique_dois.append(doi)
        return unique_dois
