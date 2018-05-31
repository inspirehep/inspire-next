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
    save_publications,
    save_signatures_and_clusters,
)


def test_save_signatures_and_clusters(isolated_app, tmpdir):
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    clusters_fd = tmpdir.join('clusters.json')
    signatures_fd = tmpdir.join('signatures.jl')

    config = {
        'DISAMBIGUATION_CLUSTERS_PATH': str(clusters_fd),
        'DISAMBIGUATION_SIGNATURES_PATH': str(signatures_fd),
    }

    with patch.dict(current_app.config, config):
        save_signatures_and_clusters()

    clusters = json.load(clusters_fd)

    assert '1010819' in clusters
    assert ['94f560d2-6791-43ec-a379-d3dc4ad0ceb7'] == clusters['1010819']

    signatures = [json.loads(line) for line in signatures_fd.readlines()]

    assert {
        'author_affiliation': 'CERN',
        'author_id': 1010819,
        'author_name': 'Ellis, John R.',
        'publication_id': 792017,
        'signature_block': 'ELj',
        'signature_uuid': '94f560d2-6791-43ec-a379-d3dc4ad0ceb7',
    } in signatures


def test_save_publications(isolated_app, tmpdir):
    TestRecordMetadata.create_from_file(__name__, '792017.json')

    publications_fd = tmpdir.join('publications.json')

    config = {'DISAMBIGUATION_PUBLICATIONS_PATH': str(publications_fd)}

    with patch.dict(current_app.config, config):
        save_publications()

    publications = json.load(publications_fd)

    assert '792017' in publications
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
    } == publications['792017']
