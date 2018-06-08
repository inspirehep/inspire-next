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
# or submit itself to any jurisdiction

"""Disambiguation API."""

from __future__ import absolute_import, division, print_function

import json
from collections import defaultdict

import six
from flask import current_app

from inspirehep.modules.disambiguation.core.db.readers import (
    get_all_curated_signatures,
    get_all_publications,
)
from inspirehep.modules.disambiguation.core.ml.models import EthnicityEstimator
from inspirehep.modules.disambiguation.utils import open_file_in_folder


def save_curated_signatures_and_input_clusters():
    """Save curated signatures and input clusters to disk.

    Saves two files to disk called (by default) ``input_clusters.jsonl`` and
    ``curated_signatures.jsonl``. The former contains one line per each cluster
    initially present in INSPIRE, while the latter contains one line per each
    curated signature that will be used as ground truth by ``BEARD``.
    """
    signatures_with_author = defaultdict(list)
    signatures_without_author = []

    with open_file_in_folder(current_app.config['DISAMBIGUATION_CURATED_SIGNATURES_PATH'], 'w') as fd:
        for signature in get_all_curated_signatures():
            if signature.get('author_id'):
                signatures_with_author[signature['author_id']].append(signature['signature_uuid'])
                fd.write(json.dumps(signature) + '\n')
            else:
                signatures_without_author.append(signature['signature_uuid'])

    with open_file_in_folder(current_app.config['DISAMBIGUATION_INPUT_CLUSTERS_PATH'], 'w') as fd:
        for cluster_id, (author_id, signature_uuids) in enumerate(six.iteritems(signatures_with_author)):
            fd.write(json.dumps({
                'author_id': author_id,
                'cluster_id': cluster_id,
                'signature_uuids': signature_uuids,
            }) + '\n')
        for cluster_id, signature_uuid in enumerate(signatures_without_author, cluster_id + 1):
            fd.write(json.dumps({
                'author_id': None,
                'cluster_id': cluster_id,
                'signature_uuids': [signature_uuid],
            }) + '\n')


def save_publications():
    """Save publications to disk.

    Saves a file to disk called (by default) ``publications.jsonl``, which
    contains one line per record in INSPIRE with information that will be
    useful for ``BEARD`` during training and prediction.
    """
    with open_file_in_folder(current_app.config['DISAMBIGUATION_PUBLICATIONS_PATH'], 'w') as fd:
        for publication in get_all_publications():
            fd.write(json.dumps(publication) + '\n')


def train_and_save_ethnicity_model():
    """Train the ethnicity estimator model and save it to disk."""
    estimator = EthnicityEstimator()
    estimator.load_data(current_app.config['DISAMBIGUATION_ETHNICITY_DATA_PATH'])
    estimator.fit()
    estimator.save_model(current_app.config['DISAMBIGUATION_ETHNICITY_MODEL_PATH'])
