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


"""Tasks for classifier."""

from __future__ import print_function

import json
import os

import cPickle as pickle

from functools import wraps

from invenio.celery import celery

from .utils import (
    update_classification_in_task_results,
    get_classification_from_task_results,
    prepare_prediction_record,
    load_model
)


def filter_core_keywords(filter_kb):
    """Filter core keywords."""
    @wraps(filter_core_keywords)
    def _filter_core_keywords(obj, eng):
        from inspire.utils.knowledge import check_keys

        result = get_classification_from_task_results(obj)
        if result is None:
            return
        filtered_core_keywords = {}
        for core_keyword, times_counted in result.get("Core keywords").items():
            if not check_keys(filter_kb, [core_keyword]):
                filtered_core_keywords[core_keyword] = times_counted
        result["Filtered Core keywords"] = filtered_core_keywords
        update_classification_in_task_results(obj, result)
    return _filter_core_keywords


def guess_coreness(model_path="core_guessing.pickle"):
    """Using a prediction model, predict if record is CORE."""
    @wraps(guess_coreness)
    def _guess_coreness(obj, eng):
        from invenio.base.globals import cfg
        from inspire.modules.classifier.core import predict

        if os.path.basename(model_path) == model_path:
            # Just the name is given, so we fill in the rest
            full_model_path = os.path.join(
                cfg.get("CLASSIFIER_MODEL_PATH"),
                model_path
            )
        else:
            # The new variable is needed due to how parameters in closures work
            full_model_path = model_path

        prepared_record = prepare_prediction_record(obj)
        pipeline = load_model(full_model_path)
        core, overall_score, top_words = predict(pipeline, prepared_record)

        result = {}
        result["core"] = core
        result["overall_score"] = overall_score
        result["top_words"] = top_words
        task_result = {
            "name": "core_guessing",
            "result": result,
            "template": "workflows/results/core_guessing.html"
        }
        obj.update_task_results(
            task_result.get("name"),
            [task_result]
        )
    return _guess_coreness


@celery.task()
def train(records, output):
    """Train a set of records and save model to file."""
    from .core import train as core_train

    records = json.load(open(records, "r"))
    if isinstance(records, dict):
        records = records.values()
    pipeline = core_train(records)
    pickle.dump(pipeline, open(output, "w"))
    print("Dumped trained model to {0}".format(output))
