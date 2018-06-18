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

"""Disambiguation core ML models."""

from __future__ import absolute_import, division, print_function

import csv
import json
import pickle

import numpy as np
from scipy.special import expit
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from beard.similarity import (
    CosineSimilarity,
    ElementMultiplication,
    EstimatorTransformer,
    PairTransformer,
    StringDistance,
)
from beard.utils import (
    FuncTransformer,
    Shaper,
    given_name,
    given_name_initial,
    normalize_name,
)
from inspire_utils.record import get_value
from inspirehep.modules.disambiguation.utils import open_file_in_folder


class EthnicityEstimator(object):
    def __init__(self, C=4.0):
        self.C = C

    def load_data(self, input_filename):
        ethnicities, lasts, firsts = [], [], []
        with open(input_filename, 'r') as fd:
            reader = csv.DictReader(fd)
            for row in reader:
                ethnicities.append(int(row['RACE']))
                lasts.append(row['NAMELAST'])
                firsts.append(row['NAMEFRST'])

        names = ['%s, %s' % (last, first) for last, first in zip(lasts, firsts)]
        normalized_names = [normalize_name(name) for name in names]

        self.X = normalized_names
        self.y = ethnicities

    def load_model(self, input_filename):
        with open(input_filename, 'r') as fd:
            self.estimator = pickle.load(fd)

    def save_model(self, output_filename):
        with open_file_in_folder(output_filename, 'w') as fd:
            pickle.dump(self.estimator, fd, protocol=pickle.HIGHEST_PROTOCOL)

    def fit(self):
        self.estimator = Pipeline([
            ('transformer', TfidfVectorizer(
                analyzer='char_wb',
                ngram_range=(1, 5),
                min_df=0.00005,
                dtype=np.float32,
                decode_error='replace',
            )),
            ('classifier', LinearSVC(C=self.C)),
        ])
        self.estimator.fit(self.X, self.y)

    def predict(self, X):
        return self.estimator.predict(X)


class DistanceEstimator(object):
    def __init__(self, ethnicity_estimator):
        self.ethnicity_estimator = ethnicity_estimator

    def load_data(self, signatures_path, pairs_path, pairs_size, publications_path):
        publications_by_id = {}
        with open(publications_path, 'r') as fd:
            for line in fd:
                publication = json.loads(line)
                publications_by_id[publication['publication_id']] = publication

        signatures_by_uuid = {}
        with open(signatures_path, 'r') as fd:
            for line in fd:
                signature = json.loads(line)
                signature['publication'] = publications_by_id[signature['publication_id']]
                signatures_by_uuid[signature['signature_uuid']] = signature

        self.X = np.empty((pairs_size, 2), dtype=np.object)
        self.y = np.empty(pairs_size, dtype=np.int)

        with open(pairs_path, 'r') as fd:
            for i, line in enumerate(fd):
                pair = json.loads(line)
                self.X[i, 0] = signatures_by_uuid[pair['signature_uuids'][0]]
                self.X[i, 1] = signatures_by_uuid[pair['signature_uuids'][1]]
                self.y[i] = 0 if pair['same_cluster'] else 1

    def load_model(self, input_filename):
        with open(input_filename, 'r') as fd:
            self.distance_estimator = pickle.load(fd)

    def save_model(self, output_filename):
        with open_file_in_folder(output_filename, 'w') as fd:
            pickle.dump(self.distance_estimator, fd, protocol=pickle.HIGHEST_PROTOCOL)

    def fit(self):
        transformer = FeatureUnion([
            ('author_full_name_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('full_name', FuncTransformer(func=get_author_full_name)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            analyzer='char_wb',
                            ngram_range=(2, 4),
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('author_second_initial_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=FuncTransformer(func=get_second_initial),
                    groupby=group_by_signature,
                )),
                ('combiner', StringDistance(similarity_function='character_equality')),
            ])),
            ('author_first_given_name_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=FuncTransformer(func=get_first_given_name),
                    groupby=group_by_signature
                )),
                ('combiner', StringDistance()),
            ])),
            ('author_second_given_name_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=FuncTransformer(func=get_second_given_name),
                    groupby=group_by_signature,
                )),
                ('combiner', StringDistance()),
            ])),
            ('author_other_names_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('other_names', FuncTransformer(func=get_author_other_names)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            analyzer='char_wb',
                            ngram_range=(2, 4),
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('affiliation_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('affiliation', FuncTransformer(func=get_author_affiliation)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            analyzer='char_wb',
                            ngram_range=(2, 4),
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('coauthors_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('coauthors', FuncTransformer(func=get_coauthors_neighborhood)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('abstract_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('abstract', FuncTransformer(func=get_abstract)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('keywords_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('keywords', FuncTransformer(func=get_keywords)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('collaborations_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('collaborations', FuncTransformer(func=get_collaborations)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('subject_similairty', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('keywords', FuncTransformer(func=get_topics)),
                        ('shaper', Shaper(newshape=(-1))),
                        ('tf-idf', TfidfVectorizer(
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('title_similarity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('title', FuncTransformer(func=get_title)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('tf-idf', TfidfVectorizer(
                            analyzer='char_wb',
                            ngram_range=(2, 4),
                            dtype=np.float32,
                            decode_error='replace',
                        )),
                    ]),
                    groupby=group_by_signature,
                )),
                ('combiner', CosineSimilarity()),
            ])),
            ('author_ethnicity', Pipeline([
                ('pairs', PairTransformer(
                    element_transformer=Pipeline([
                        ('name', FuncTransformer(func=get_author_full_name)),
                        ('shaper', Shaper(newshape=(-1,))),
                        ('classifier', EstimatorTransformer(self.ethnicity_estimator.estimator)),
                    ]),
                    groupby=group_by_signature,
                )),
                ('sigmoid', FuncTransformer(func=expit)),
                ('combiner', ElementMultiplication()),
            ])),
        ])
        classifier = RandomForestClassifier(n_estimators=500, n_jobs=8)

        self.distance_estimator = Pipeline([('transformer', transformer), ('classifier', classifier)])
        self.distance_estimator.fit(self.X, self.y)


def get_author_full_name(signature):
    return normalize_name(signature['author_name'])


def get_first_initial(signature):
    try:
        return given_name_initial(signature['author_name'], 0)
    except IndexError:
        return ''


def get_second_initial(signature):
    try:
        return given_name_initial(signature['author_name'], 1)
    except IndexError:
        return ''


def get_first_given_name(signature):
    return given_name(signature['author_name'], 0)


def get_second_given_name(signature):
    return given_name(signature['author_name'], 1)


def get_author_other_names(signature):
    author_name = signature['author_name']
    other_names = author_name.split(',', 1)
    return normalize_name(other_names[1]) if len(other_names) == 2 else ''


def get_author_affiliation(signature):
    author_affiliation = signature['author_affiliation']
    return normalize_name(author_affiliation) if author_affiliation else ''


def get_coauthors_neighborhood(signature, radius=10):
    authors = get_value(signature, 'publication.authors', default=[])
    try:
        center = authors.index(signature['author_name'])
        return ' '.join(authors[max(0, center - radius):min(len(authors), center + radius)])
    except ValueError:
        return ' '.join(authors)


def get_abstract(signature):
    return get_value(signature, 'publication.abstract', default='')


def get_keywords(signature):
    return ' '.join(get_value(signature, 'publication.keywords', default=[]))


def get_collaborations(signature):
    return ' '.join(get_value(signature, 'publication.collaborations', default=[]))


def get_topics(signature):
    return ' '.join(get_value(signature, 'publication.topics', default=[]))


def get_title(signature):
    return get_value(signature, 'publication.title', default='')


def group_by_signature(signatures):
    return signatures[0]['signature_uuid']
