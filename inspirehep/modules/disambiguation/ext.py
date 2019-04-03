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

"""Disambiguation extension."""

from __future__ import absolute_import, division, print_function

import os

from . import config


class InspireDisambiguation(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.init_config(app)
        app.extensions['inspire-disambiguation'] = self

    def init_config(self, app):
        disambiguation_base_path = os.path.join(app.instance_path, 'disambiguation')

        app.config['DISAMBIGUATION_BASE_PATH'] = disambiguation_base_path
        app.config['DISAMBIGUATION_CURATED_SIGNATURES_PATH'] = os.path.join(
            disambiguation_base_path, 'curated_signatures.jsonl')
        app.config['DISAMBIGUATION_INPUT_CLUSTERS_PATH'] = os.path.join(
            disambiguation_base_path, 'input_clusters.jsonl')
        app.config['DISAMBIGUATION_SAMPLED_PAIRS_PATH'] = os.path.join(
            disambiguation_base_path, 'sampled_pairs.jsonl')
        app.config['DISAMBIGUATION_PUBLICATIONS_PATH'] = os.path.join(
            disambiguation_base_path, 'publications.jsonl')
        app.config['DISAMBIGUATION_ETHNICITY_DATA_PATH'] = os.path.join(
            disambiguation_base_path, 'ethnicity.csv')
        app.config['DISAMBIGUATION_ETHNICITY_MODEL_PATH'] = os.path.join(
            disambiguation_base_path, 'ethnicity.pkl')
        app.config['DISAMBIGUATION_DISTANCE_MODEL_PATH'] = os.path.join(
            disambiguation_base_path, 'distance.pkl')
        app.config['DISAMBIGUATION_CLUSTERING_MODEL_PATH'] = os.path.join(
            disambiguation_base_path, 'clustering.pkl')

        for k in dir(config):
            if k.startswith('DISAMBIGUATION_'):
                app.config.setdefault(k, getattr(config, k))
