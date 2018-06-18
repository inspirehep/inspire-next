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
import pickle

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from beard.utils import normalize_name
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
