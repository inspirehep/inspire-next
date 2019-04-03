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

"""Disambiguation core ML sampling."""

from __future__ import absolute_import, division, print_function

import itertools
import json
import random

from collections import defaultdict


class IncompleteSamplingError(Exception):
    pass


def sample_signature_pairs(signatures_path, clusters_path, pairs_size):
    """Sample signature pairs to generate less training data.

    Since INSPIRE contains ~3M curated signatures it would take too much time
    to train on all possible pairs, so we sample a subset in such a way that
    they are representative of the known cluster structure.

    This is accomplished in three steps:

        1. First we read all the clusters and signatures and build in-memory
           data structures to perform fast lookups of the id of the cluster
           to which a signature belongs as well as lookups of the name of the
           author associated with the signature.

           At the same time we partition the signatures in blocks according
           to the phonetic encoding of the name. Note that two signatures
           pointing to two distinct authors might end up in the same block.

        2. Then we classify signature pairs that belong to the same block
           according to whether they belong to same cluster and whether they
           share the same author name.

           The former is because we want to have both examples of pairs of
           signatures in the same block pointing to the same author and
           different authors, while the latter is to avoid oversampling the
           typical case of signatures with exactly the same author name.

        3. Finally we sample from each of the non-empty resulting categories
           an equal portion of the desired number of pairs. Note that this
           requires that it must be divisible by 12, the LCM of the possible
           number of non-empty categories, to make sure that we will sample
           the same number of pairs from each category.

    Yields:
        dict: a signature pair.

    """

    #
    # 1. Read & Build
    #

    blocks_and_uuids = []
    blocks = defaultdict(list)
    author_names_by_signature_uuid = {}
    with open(signatures_path, 'r') as fd:
        for line in fd:
            signature = json.loads(line)
            blocks[signature['signature_block']].append(signature['signature_uuid'])
            blocks_and_uuids.append((signature['signature_block'], signature['signature_uuid']))
            author_names_by_signature_uuid[signature['signature_uuid']] = signature['author_name']

    cluster_ids_by_signature_uuid = {}
    with open(clusters_path, 'r') as fd:
        for line in fd:
            cluster = json.loads(line)
            for signature_uuid in cluster['signature_uuids']:
                cluster_ids_by_signature_uuid[signature_uuid] = cluster['cluster_id']

    #
    # 2. Monte Carlo sampling for efficiency
    #

    def same_cluster(s1, s2):
        return cluster_ids_by_signature_uuid[s1] == cluster_ids_by_signature_uuid[s2]

    def same_name(s1, s2):
        return author_names_by_signature_uuid[s1] == author_names_by_signature_uuid[s2]

    max_iterations = len(blocks_and_uuids)**2
    counts = {
        (True, True): 0,
        (True, False): 0,
        (False, True): 0,
        (False, False): 0,
    }

    iterations = 0
    while any(count < pairs_size // 4 for count in counts.values()) and iterations < max_iterations:
        iterations += 1
        block, s1 = random.choice(blocks_and_uuids)
        s2 = random.choice(blocks[block])
        if s1 == s2:
            continue
        kind = (same_cluster(s1, s2), same_name(s1, s2))
        if counts[kind] < pairs_size // 4:
            counts[kind] += 1
            yield {'same_cluster': kind[0], 'signature_uuids': [s1, s2]}

    if iterations == max_iterations:
        raise IncompleteSamplingError(
            'Could not generate {} samples, only managed to generate {} in reasonable time.'
            ' Generated samples are probably unbalanced.'.format(pairs_size, sum(counts.values()))
        )
