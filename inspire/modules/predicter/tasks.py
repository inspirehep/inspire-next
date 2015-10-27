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

from invenio_celery import celery

from inspire.utils.helpers import (
    get_record_from_model,
)

from .utils import (
    prepare_prediction_record,
    load_model
)


def guess_coreness(model_path="arxiv_guessing.pickle", top_words=0):
    """Using a prediction model, predict if record is CORE."""
    @wraps(guess_coreness)
    def _guess_coreness(obj, eng):
        from invenio_base.globals import cfg
        from .arxiv import predict

        if os.path.basename(model_path) == model_path:
            # Just the name is given, so we fill in the rest
            full_model_path = os.path.join(
                cfg.get("CLASSIFIER_MODEL_PATH"),
                model_path
            )
        else:
            # The new variable is needed due to how parameters in closures work
            full_model_path = model_path

        if not os.path.isfile(full_model_path):
            obj.log.error(
                "Model file {0} not found! Skipping prediction...".format(
                    full_model_path
                )
            )
            return
        model = eng.workflow_definition.model(obj)
        record = get_record_from_model(model)

        prepared_record = prepare_prediction_record(record)

        pipeline = load_model(full_model_path)

        result = {}
        if not top_words:
            decision, scores = predict(pipeline, prepared_record, top_words)
        else:
            decision, scores, top_core, top_noncore, top_rejected = \
                predict(pipeline, prepared_record, top_words)
            result["top_core"] = top_core
            result["top_noncore"] = top_noncore
            result["top_rejected"] = top_rejected

        obj.log.info("Successfully predicted as {0} with {1}".format(decision, max(scores)))

        result["decision"] = decision
        result["max_score"] = max(scores)
        result["all_scores"] = scores
        task_result = {
            "name": "arxiv_guessing",
            "result": result,
            "template": "workflows/results/arxiv_guessing.html"
        }
        obj.update_task_results(
            task_result.get("name"),
            [task_result]
        )
    return _guess_coreness


@celery.task()
def train(records, output, skip_categories=True, skip_astro=True):
    """Train a set of records and save model to file."""
    from .arxiv import train as core_train

    records = json.load(open(records, "r"))
    if isinstance(records, dict):
        records = records.values()
    print("Records found: {0}".format(len(records)))
    if skip_astro:
        astro_categories = {
            'astro-ph.SR',
            'astro-ph',
            'astro-ph.EP',
            'astro-ph.IM',
            'astro-ph.GA'
        }
        records = [r for r in records
                   if not (astro_categories & set(r["categories"]) and not
                           (r["id"].startswith("14") or r["id"].startswith("15")))]
        print("Records after filtering: {0}".format(len(records)))
    pipeline = core_train(records, not skip_categories)
    pickle.dump(pipeline, open(output, "w"))
    print("Dumped trained model to {0}".format(output))
