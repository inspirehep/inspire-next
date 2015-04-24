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


"""Automatic tagging of CORE papers.

Usage:
    python core.py mode record_file model_file
    - mode: train or predict
    - record_file:
        JSON file holding records.
    - model_file:
        File into which is the model is saved (`mode == "train"`),
        or loaded from (`mode == "predict"`).

Examples:
    python core.py train records.json model.pickle
    python core.py predict records.json model.pickle
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


def _get_journal(r):
    return r["journal"] if r["journal"] else ""


def _get_collaborations(r):
    return " ".join(r["collaborations"])


def _get_keywords(r):
    return " ".join(r["keywords"])


def _get_abstract(r):
    return r["abstract"] if r["abstract"] else ""


def train(records):
    """Train a CORE-tagging classifier on the given records.

    :param records:
        Records are expected as a list of dictionaries with
        the following fields required: "title", "journal", "collaborations",
        "keywords", "abstract" and "core".

        Example:
            records = [{u'core': True,
                        u'title': u'Effects of top compositeness',
                        u'collaborations': [],
                        u'abstract': u'We investigate the effects of (...)',
                        u'keywords': [u'numerical calculations',
                                      u'effective Lagrangian', ...],
                        u'journal': u'Phys.Rev.'}, {...}, ...]

    :return: the trained pipeline
    """
    records = np.array(records, dtype=np.object).reshape((-1, 1))

    transformer = Pipeline([
        ("features", FeatureUnion([
            ("title", Pipeline([
                ("get_title", FuncTransformer(func=_get_title)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(binary=True, min_df=0.00005,
                                          max_df=0.9, stop_words="english",
                                          dtype=np.float32,
                                          decode_error="replace"))])),
            ("journal", Pipeline([
                ("get_journal", FuncTransformer(func=_get_journal)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(binary=True, dtype=np.float32,
                                          decode_error="replace"))])),
            ("collaborations", Pipeline([
                ("get_collaborations",
                    FuncTransformer(func=_get_collaborations)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(binary=True, dtype=np.float32,
                                          decode_error="replace"))])),
            ("keywords", Pipeline([
                ("get_keywords", FuncTransformer(func=_get_keywords)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(binary=True, min_df=0.00005,
                                          max_df=0.9, stop_words="english",
                                          dtype=np.float32,
                                          decode_error="replace"))])),
            ("abstract", Pipeline([
                ("get_abstract", FuncTransformer(func=_get_abstract)),
                ("shape", Shaper(newshape=(-1,))),
                ("tfidf", TfidfVectorizer(binary=True, min_df=0.00005,
                                          max_df=0.9, stop_words="english",
                                          dtype=np.float32,
                                          decode_error="replace"))])),
        ])),
        ("scaling", Normalizer())
    ])

    X = transformer.fit_transform(records)
    y = np.array([r[0]["core"] for r in records])

    grid = GridSearchCV(LinearSVC(),
                        param_grid={"C": np.linspace(start=0.01, stop=1.0,
                                                     num=100)},
                        scoring="accuracy", cv=5, verbose=3)
    grid.fit(X, y)

    return Pipeline([("transformer", transformer),
                     ("classifier", grid.best_estimator_)])


def _feature_to_word(transformer):
    mapping = []

    for field, step in transformer.named_steps["features"].transformer_list:
        features = step.named_steps["tfidf"].get_feature_names()
        mapping.append((field, features))

    return mapping


def _top_words(scores, mapping, limit=20):
    scores = sorted(scores, key=lambda x: -abs(x[1]))
    words = []

    for j, s in scores[:limit]:
        for field, features in mapping:
            if j < len(features):
                words.append((field, features[j], s))
                break
            else:
                j -= len(features)

    return words


def predict(pipeline, record):
    """Predict whether the given record is CORE or not.

    :param record:
        Record is expected as a dictionary with
        the following fields required: "title", "journal", "collaborations",
        "keywords" and "abstract".

        Example:
            record = [{u'title': u'Effects of top compositeness',
                       u'collaborations': [],
                       u'abstract': u'We investigate the effects of (...)',
                       u'keywords': [u'numerical calculations',
                                     u'effective Lagrangian', ...],
                       u'journal': u'Phys.Rev.'}

    :return core, overall_score, top_words:
        core: whether the record is predicted as CORE or not
        overall_score: the decision score
        top_words: the top words, as an ordered list of (field, word, score)
                   tuples

        Example:
            (True,
             1.8648841450487654,
             [('abstract', u'quark', 0.18866499890979657),
              ('keywords', u'graph', 0.17593287718481129),
              ('keywords', u'feynman', 0.13165504098727204), ...])
    """
    transformer = pipeline.steps[0][1]
    classifier = pipeline.steps[1][1]

    X = transformer.transform(np.array([[record]], dtype=np.object))

    mapping = _feature_to_word(transformer)
    scores = []

    for _, j in zip(*X[0].nonzero()):
        s = classifier.coef_[0, j] * X[0, j]
        scores.append((j, s))

    top_words = _top_words(scores, mapping)
    overall_score = classifier.intercept_[0] + sum(s for _, s in scores)

    return overall_score > 0., overall_score, top_words


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
