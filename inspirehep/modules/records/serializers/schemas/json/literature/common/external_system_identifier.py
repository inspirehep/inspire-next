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

from marshmallow import Schema, post_dump, fields, missing


class ExternalSystemIdentifierSchemaV1(Schema):
    url_name = fields.Method('get_url_name')
    url_link = fields.Method('get_url_link')

    schema_to_url_name_map = {
        'ads': 'ADS Abstract Service',
        'cds': 'CERN Document Server',
        'euclid': 'Project Euclid',
        'hal': 'HAL Archives Ouvertes',
        'kekscan': 'KEK scanned document',
        'msnet': 'AMS MathSciNet',
        'osti': 'OSTI Information Bridge Server',
        'zblatt': 'zbMATH'
    }

    schema_to_url_link_prefix_map = {
        'ads': 'http://adsabs.harvard.edu/abs/',
        'cds': 'http://cds.cern.ch/record/',
        'euclid': 'http://projecteuclid.org/',
        'hal': 'https://hal.archives-ouvertes.fr/',
        'kekscan': 'https://lib-extopc.kek.jp/preprints/PDF/',
        'msnet': 'http://www.ams.org/mathscinet-getitem?mr=',
        'osti': 'https://www.osti.gov/scitech/biblio/',
        'zblatt': 'http://www.zentralblatt-math.org/zmath/en/search/?an='
    }

    def get_url_name(self, data):
        schema = data.get('schema').lower()
        url_name = self.schema_to_url_name_map.get(schema)
        if url_name is None:
            return missing
        return url_name

    def get_url_link(self, data):
        schema = data.get('schema').lower()
        value = data.get('value')
        url_prefix = self.schema_to_url_link_prefix_map.get(schema)
        if url_prefix is None:
            return missing
        if schema == 'kekscan':
            kekscan_link = self.get_link_for_kekscan_schema(value)
            if kekscan_link is None:
                return missing
            return kekscan_link
        return '{}{}'.format(url_prefix, value)

    def get_link_for_kekscan_schema(self, external_system_id_value):
        extid = external_system_id_value.replace('-', '')
        if len(extid) == 7 and not extid.startswith('19') and not extid.startswith('20'):
            year = '19' + extid[:2]
        elif len(extid) == 9:
            year = extid[:4]
            extid = extid[2:]
        else:
            return None
        yymm = extid[:4]
        kekscan_url_prefix = self.schema_to_url_link_prefix_map['kekscan']
        return '{}{}/{}/{}.pdf'.format(kekscan_url_prefix, year, yymm, extid)

    @post_dump(pass_many=True)
    def filter(self, data, many):
        if not many:
            if self.is_missing_url_name_or_link(data):
                return {}
            return data
        data = self.take_ids_that_have_all_fields(data)
        data = self.take_first_id_foreach_url_name(data)
        return data

    def take_ids_that_have_all_fields(self, external_system_ids):
        return [extid for extid in external_system_ids
                if not self.is_missing_url_name_or_link(extid)]

    def is_missing_url_name_or_link(self, external_system_id):
        return external_system_id.get('url_link') is None \
            or external_system_id.get('url_name') is None

    def take_first_id_foreach_url_name(self, external_system_ids):
        taken_url_names = set()
        unique_ids = []
        for external_system_id in external_system_ids:
            url_name = external_system_id.get('url_name')
            if url_name not in taken_url_names:
                taken_url_names.add(url_name)
                unique_ids.append(external_system_id)
        return unique_ids
