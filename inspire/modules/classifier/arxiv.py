# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""Automatic selection of arXiv papers for inclusion in Inspire.

Usage:
    python arXiv.py mode record_file model_file
    - mode: train or predict
    - record_file:
        JSON file holding records.
    - model_file:
        File into which is the model is saved (`mode == "train"`),
        or loaded from (`mode == "predict"`).

Examples:
    python arxiv.py train records.json model.pickle
    python arxiv.py predict records.json model.pickle
"""


import numpy as np
import cPickle as pickle

from beard.utils import FuncTransformer
from beard.utils import Shaper

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn.svm import LinearSVC


def _get_title(r):
    return r["title"] if r["title"] else ""


def _get_abstract(r):
    return r["abstract"] if r["abstract"] else ""


def _get_title_abstract(r):
    return _get_title(r) + " " + _get_abstract(r)


def _get_categories(r):
    return " ".join(r["categories"])


def train(records):
    """Train a classifier on the given arXiv records.

    :param records:
        Records are expected as a list of dictionaries with
        the following fields required: "title", "abstract", "categories"
        and "decision". The decision field should be either "CORE", "Non-CORE"
        or "Rejected".

        Example:
            records = [{u'decision': "CORE",
                        u'title': u'Effects of top compositeness',
                        u'abstract': u'We investigate the effects of (...)'
                        u'categories': [u'cond-mat.mes-hall',
                                        u'cond-mat.mtrl-sci']},
                        {...}, ...]

    :return: the trained pipeline
    """
    records = np.array(records, dtype=np.object).reshape((-1, 1))

    transformer = Pipeline([
        ("features", FeatureUnion([
            ("title_abstract", Pipeline([
                ("getter", FuncTransformer(func=_get_title_abstract)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(min_df=3, max_df=0.1, norm="l2",
                                          ngram_range=(1, 1),
                                          stop_words="english",
                                          strip_accents="unicode",
                                          dtype=np.float32,
                                          decode_error="replace"))])),
            ("categories", Pipeline([
                ("getter", FuncTransformer(func=_get_categories)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(norm="l2", dtype=np.float32,
                                          decode_error="replace"))])),
        ])),
        ("scaling", Normalizer())
    ])

    X = transformer.fit_transform(records)
    y = np.array([r[0]["decision"] for r in records])

    grid = GridSearchCV(LinearSVC(),
                        param_grid={"C": np.linspace(start=0.1, stop=1.0,
                                                     num=100)},
                        scoring="accuracy", cv=5, verbose=3)
    grid.fit(X, y)

    return Pipeline([("transformer", transformer),
                     ("classifier", grid.best_estimator_)])


def predict(pipeline, record):
    """Predict whether the given record is CORE/Non-CORE/Rejected.

    :param record:
        Record is expected as a dictionary with
        the following fields required: "title", "abstract", "categories".

        Example:
            record = {u'title': u'Effects of top compositeness',
                      u'abstract': u'We investigate the effects of (...)'
                      u'categories': [u'cond-mat.mes-hall',
                                      u'cond-mat.mtrl-sci']}

    :return decision, scores:
        decision: CORE, Non-CORE or Rejected, as the argmax of scores
        scores: the decision scores

        Example:
            (u'Rejected', array([-1.25554232, -1.2591557, 1.17074973]))
    """
    transformer = pipeline.steps[0][1]
    classifier = pipeline.steps[1][1]

    X = transformer.transform(np.array([[record]], dtype=np.object))

    decision = classifier.predict(X)[0]
    scores = classifier.decision_function(X)[0]

    return decision, scores


if __name__ == "__main__":
    import json
    import sys

    mode = sys.argv[1]

    records = json.load(open(sys.argv[2], "r"))
    if isinstance(records, dict):
        records = records.values()

    if mode == "train":
        pipeline = train(records)
        pickle.dump(pipeline, open(sys.argv[3], "w"))

    elif mode == "predict":
        pipeline = pickle.load(open(sys.argv[3]))

        for r in records[:5]:
            print r
            print predict(pipeline, r)
            print
