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
from sklearn.metrics import euclidean_distances
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


def train(records, use_categories=True):
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

    :param use_categories:
        Whether the "categories" is used to build the classifier.

    :return: the trained pipeline
    """
    records = np.array(records, dtype=np.object).reshape((-1, 1))

    if use_categories:
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

    else:
        transformer = Pipeline([
            ("getter", FuncTransformer(func=_get_title_abstract)),
            ("shape", Shaper(newshape=(-1,))),
            ("tfidf", TfidfVectorizer(min_df=3, max_df=0.1, norm="l2",
                                      ngram_range=(1, 1),
                                      stop_words="english",
                                      strip_accents="unicode",
                                      dtype=np.float32,
                                      decode_error="replace")),
            ("scaling", Normalizer())
        ])

    X = transformer.fit_transform(records)
    y = np.array([r[0]["decision"] for r in records])

    # FIXME: Perhaps add , n_jobs=-1 for parallel jobs
    grid = GridSearchCV(LinearSVC(),
                        param_grid={"C": np.linspace(start=0.2, stop=0.5,
                                                     num=20)},
                        scoring="accuracy", cv=3, verbose=3)
    grid.fit(X, y)

    return Pipeline([("transformer", transformer),
                     ("classifier", grid.best_estimator_)])


def predict(pipeline, record, top_words=0):
    """Predict whether the given record is CORE/Non-CORE/Rejected.

    :param pipeline:
        A classification pipeline, as returned by ``train``.

    :param record:
        Record is expected as a dictionary with
        the following fields required: "title", "abstract", "categories".

        Example:
            record = {u'title': u'Effects of top compositeness',
                      u'abstract': u'We investigate the effects of (...)'
                      u'categories': [u'cond-mat.mes-hall',
                                      u'cond-mat.mtrl-sci']}

    :param top_words:
        The top words explaining the classifier decision.

    :return decision, scores:
        decision: CORE, Non-CORE or Rejected, as the argmax of scores
        scores: the decision scores

        if ``top_words > 0``, then ``top_core``, ``top_noncore`` and
        ``top_rejected`` are additionally returned. Each is a list
        of ``top_words`` (word, weight) pairs corresponding to the
        words explaining the classifier decision.

        Example:
            (u'Rejected', array([-1.25554232, -1.2591557, 1.17074973]))
    """
    transformer = pipeline.steps[0][1]
    classifier = pipeline.steps[1][1]

    X = transformer.transform(np.array([[record]], dtype=np.object))

    decision = classifier.predict(X)[0]
    scores = classifier.decision_function(X)[0]

    if top_words == 0:
        return decision, scores

    else:
        top_core, top_noncore, top_rejected = [], [], []

        if len(transformer.steps) == 2:
            tf1 = transformer.steps[0][1].transformer_list[0][1].steps[2][1]
            tf2 = transformer.steps[0][1].transformer_list[1][1].steps[2][1]
            inv_vocabulary = {v: k for k, v in tf1.vocabulary_.items()}
            inv_vocabulary.update({v + len(tf1.vocabulary_): k
                                   for k, v in tf2.vocabulary_.items()})

        else:
            tf1 = transformer.steps[2][1]
            inv_vocabulary = {v: k for k, v in tf1.vocabulary_.items()}

        for i, j in zip(*X.nonzero()):
            top_core.append((inv_vocabulary[j],
                             classifier.coef_[0][j] * X[0, j]))
            top_noncore.append((inv_vocabulary[j],
                                classifier.coef_[1][j] * X[0, j]))
            top_rejected.append((inv_vocabulary[j],
                                 classifier.coef_[2][j] * X[0, j]))

        top_core = sorted(top_core,
                          reverse=True, key=lambda x: x[1])[:top_words]
        top_noncore = sorted(top_noncore,
                             reverse=True, key=lambda x: x[1])[:top_words]
        top_rejected = sorted(top_rejected,
                              reverse=True, key=lambda x: x[1])[:top_words]
        return decision, scores, top_core, top_noncore, top_rejected


def closest(pipeline, records, record, n=10):
    """Find the closest records from the given record.

    :param pipeline:
        A classification pipeline, as returned by ``train``.

    :param records:
        Records are expected as a list of dictionaries.

    :param record:
        Record is expected as a dictionary.

    :param n:
        The number of closest records to return.

    :return list:
        The ``n`` closest records.
    """
    transformer = pipeline.steps[0][1]

    X = transformer.transform(np.array(records, dtype=np.object))
    X_record = transformer.transform(np.array([record], dtype=np.object))
    top = np.argsort(euclidean_distances(X, X_record), axis=0)

    return [records[i] for i in top[:n]]


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
