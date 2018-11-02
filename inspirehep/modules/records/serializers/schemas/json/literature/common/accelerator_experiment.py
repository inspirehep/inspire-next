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

from inspire_dojson.utils import get_recid_from_ref
from inspire_utils.record import get_value
from inspire_utils.helpers import force_list
from inspirehep.modules.records.utils import get_linked_records_in_field


class AcceleratorExperimentSchemaV1(Schema):

    name = fields.Method('get_name')

    @pre_dump(pass_many=True)
    def resolve_experiment_records(self, data, many):
        experiment_records_map = self.get_control_numbers_to_resolved_experiments_map(
            data)
        if not many:
            return self.get_resolved_record_or_experiment(
                experiment_records_map, data)

        return [self.get_resolved_record_or_experiment(experiment_records_map, experiment)
                for experiment in data]

    def get_control_numbers_to_resolved_experiments_map(self, data):
        data = force_list(data)
        resolved_records = get_linked_records_in_field(
            {'accelerator_experiments': data}, 'accelerator_experiments.record'
        )
        return {
            record['control_number']: record
            for record in resolved_records
        }

    def get_resolved_record_or_experiment(self, experiment_records_map, experiment):
        experiment_record_id = get_recid_from_ref(experiment.get('record'))
        experiment_record = experiment_records_map.get(experiment_record_id)
        return experiment_record or experiment

    def get_name(self, item):
        institution = get_value(item, 'institutions[0].value')
        accelerator = get_value(item, 'accelerator.value')
        experiment = get_value(item, 'experiment.value')
        if institution and accelerator and experiment:
            return '{}-{}-{}'.format(institution, accelerator, experiment)
        return item.get('legacy_name')
