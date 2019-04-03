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

import six

from collections import defaultdict

from six.moves import range


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

    blocks = defaultdict(list)
    author_names_by_signature_uuid = {}
    with open(signatures_path, 'r') as fd:
        for line in fd:
            signature = json.loads(line)
            blocks[signature['signature_block']].append(signature['signature_uuid'])
            author_names_by_signature_uuid[signature['signature_uuid']] = signature['author_name']

    cluster_ids_by_signature_uuid = {}
    with open(clusters_path, 'r') as fd:
        for line in fd:
            cluster = json.loads(line)
            for signature_uuid in cluster['signature_uuids']:
                cluster_ids_by_signature_uuid[signature_uuid] = cluster['cluster_id']

    #
    # 2. Classify
    #

    def same_cluster(s1, s2):
        return cluster_ids_by_signature_uuid[s1] == cluster_ids_by_signature_uuid[s2]

    def same_name(s1, s2):
        return author_names_by_signature_uuid[s1] == author_names_by_signature_uuid[s2]

    same_cluster_same_name = (
        {'same_cluster': True, 'signature_uuids': [s1, s2]} for (s1, s2)
        in all_signature_pairs(blocks) if same_cluster(s1, s2) and same_name(s1, s2)
    )
    same_cluster_different_name = (
        {'same_cluster': True, 'signature_uuids': [s1, s2]} for (s1, s2)
        in all_signature_pairs(blocks) if same_cluster(s1, s2) and not same_name(s1, s2)
    )
    different_cluster_same_name = (
        {'same_cluster': False, 'signature_uuids': [s1, s2]} for (s1, s2)
        in all_signature_pairs(blocks) if not same_cluster(s1, s2) and same_name(s1, s2)
    )
    different_cluster_different_name = (
        {'same_cluster': False, 'signature_uuids': [s1, s2]} for (s1, s2)
        in all_signature_pairs(blocks) if not same_cluster(s1, s2) and not same_name(s1, s2)
    )

    #
    # 3. Sample
    #

    non_empty_categories = [
        category for category in [
            same_cluster_same_name,
            same_cluster_different_name,
            different_cluster_same_name,
            different_cluster_different_name,
        ] if any(True for _ in category)  # check whether iterator is non-empty (consumes first element but there are plenty)
    ]
    for category in non_empty_categories:
        for pair in sample_from_iter(category, pairs_size // len(non_empty_categories)):
            yield pair


def all_signature_pairs(blocks):
    return itertools.chain.from_iterable(itertools.combinations(block, 2) for block in six.itervalues(blocks))


def sample_from_iter(iterable, samplesize):
    """Uniformly sample samplesize elements from iterable.

    This uses reservoir sampling to avoid loading the full iterable in memory.
    Taken from https://stackoverflow.com/a/12583436 (with no shuffling).
    """ 
    results = []
    iterator = iter(iterable)
    # Fill in the first samplesize elements:
    try:
        for _ in range(samplesize):
            results.append(iterator.next())
    except StopIteration:
        raise ValueError("Sample larger than population.")
    for i, v in enumerate(iterator, samplesize):
        r = random.randint(0, i)
        if r < samplesize:
            results[r] = v  # at a decreasing rate, replace random items
    return results
