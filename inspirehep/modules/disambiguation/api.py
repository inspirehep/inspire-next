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

from flask import current_app

from inspirehep.modules.disambiguation.core.db.readers import get_all_curated_signatures


def save_training_data():
    """Save training data to disk.

    Saves two files to disk called (by default) ``clusters.json`` and ``signatures.json``.
    The former contains a dictionary that represents the starting clusters that are used
    by BEARD as ground truth, while the latter contains one line per curated signature
    present in INSPIRE.

    """
    clusters = defaultdict(list)

    with open(current_app.config['DISAMBIGUATION_SIGNATURES_PATH'], 'w') as fd:
        for signature in get_all_curated_signatures():
            if signature.get('author_id'):
                clusters[signature['author_id']].append(signature['signature_uuid'])
                fd.write(json.dumps(signature) + '\n')

    with open(current_app.config['DISAMBIGUATION_CLUSTERS_PATH'], 'w') as fd:
        json.dump(clusters, fd)
