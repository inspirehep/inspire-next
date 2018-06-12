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

import json
from mock import patch

from flask import current_app

from factories.db.invenio_records import TestRecordMetadata

from inspirehep.modules.disambiguation.api import (
    save_curated_signatures_and_input_clusters,
    save_publications,
    train_and_save_ethnicity_model,
)
from inspirehep.modules.disambiguation.core.ml.models import EthnicityEstimator

TRAINING_DATA = '''\
RACE,NAMELAST,NAMEFRST
1,EASTWOOD,CLINT
5,MIFUNE,TOSHIRO
'''


def test_save_curated_signatures_and_input_clusters(isolated_app, tmpdir):
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    curated_signatures_fd = tmpdir.join('curated_signatures.jsonl')
    input_clusters_fd = tmpdir.join('input_clusters.jsonl')

    config = {
        'DISAMBIGUATION_CURATED_SIGNATURES_PATH': str(curated_signatures_fd),
        'DISAMBIGUATION_INPUT_CLUSTERS_PATH': str(input_clusters_fd),
    }

    with patch.dict(current_app.config, config):
        save_curated_signatures_and_input_clusters()

    input_clusters = [json.loads(line) for line in input_clusters_fd.readlines()]
    reversed_input_clusters = {
        input_cluster['cluster_id']: {
            'author_id': input_cluster['author_id'],
            'signature_uuids': input_cluster['signature_uuids'],
        } for input_cluster in input_clusters
    }  # XXX: so that the assertion doesn't depend on cluster_id.

    assert {
        'author_id': 1010819,
        'signature_uuids': ['94f560d2-6791-43ec-a379-d3dc4ad0ceb7'],
    } in reversed_input_clusters.values()

    curated_signatures = [json.loads(line) for line in curated_signatures_fd.readlines()]

    assert {
        'author_affiliation': 'CERN',
        'author_id': 1010819,
        'author_name': 'Ellis, John R.',
        'publication_id': 792017,
        'signature_block': 'ELj',
        'signature_uuid': '94f560d2-6791-43ec-a379-d3dc4ad0ceb7',
    } in curated_signatures


def test_save_publications(isolated_app, tmpdir):
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    publications_fd = tmpdir.join('publications.jsonl')

    config = {'DISAMBIGUATION_PUBLICATIONS_PATH': str(publications_fd)}

    with patch.dict(current_app.config, config):
        save_publications()

    publications = [json.loads(line) for line in publications_fd.readlines()]

    assert {
        'abstract': 'This talk describes past progress in probing the structure of matter and the content of the Universe, which has led to the Standard Model of elementary particles, and the prospects for establishing new physics beyond the Standard Model using the LHC particle collider at CERN.',
        'authors': ['Ellis, John R.'],
        'collaborations': [],
        'keywords': [
            '29.20.Db',
            '98.80.-k',
            '12.60.-i',
            'elementary particles',
            'standard model',
            'cosmology',
            'particle accelerators',
            'Elementary particles',
            'Beyond the Standard Model',
            'Colliders',
            'Large Hadron Collider',
            'Standard Model',
        ],
        'publication_id': 792017,
        'title': 'The quest for elementary particles',
        'topics': ['Phenomenology-HEP'],
    } in publications


def test_train_and_save_ethnicity_model(tmpdir):
    ethnicity_data_fd = tmpdir.join('ethnicity.csv')
    ethnicity_data_fd.write(TRAINING_DATA)
    ethnicity_model_fd = tmpdir.join('ethnicity.pkl')

    config = {
        'DISAMBIGUATION_ETHNICITY_DATA_PATH': str(ethnicity_data_fd),
        'DISAMBIGUATION_ETHNICITY_MODEL_PATH': str(ethnicity_model_fd),
    }

    with patch.dict(current_app.config, config):
        train_and_save_ethnicity_model()

    estimator = EthnicityEstimator()
    estimator.load_model(str(ethnicity_model_fd))
    estimator.predict(['Guinness, Alec'])
