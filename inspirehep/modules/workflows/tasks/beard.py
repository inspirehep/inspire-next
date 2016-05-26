# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Set of workflow tasks for beard API."""

from __future__ import absolute_import, print_function

import requests

from flask import current_app

from inspirehep.utils.record import get_value

from inspirehep.modules.workflows.utils import json_api_request


def prepare_payload(record):
    """Prepare payload to send to Beard API."""
    payload = dict(title="", abstract="", categories=[])
    titles = filter(None, get_value(record, "titles.title", []))
    # FIXME May have to normalize categories in the future
    arxiv_categories = map(
        lambda x: x[0],
        filter(None, get_value(record, "arxiv_eprints.categories", []))
    )
    if titles:
        payload['title'] = titles[0]
    abstracts = filter(None, get_value(record, "abstracts.value", []))
    if abstracts:
        payload['abstracts'] = abstracts[0]
    if arxiv_categories:
        payload['categories'] = arxiv_categories
    return payload


def guess_coreness(obj, eng):
    """Workflow task to ask Beard API for a coreness assessment."""
    base_url = current_app.config.get("BEARD_API_URL")
    if not base_url:
        # Skip task if no API URL set
        return
    predictor_url = "{base_url}/predictor/coreness".format(
        base_url=base_url
    )
    # FIXME: Have option to select different prediction models when
    # available in the API
    payload = prepare_payload(obj.data)
    try:
        results = json_api_request(predictor_url, payload)
    except requests.exceptions.RequestException:
        # We still continue even if there was an exception.
        pass
    if results:
        scores = results.get('scores') or []
        max_score = max(scores)
        decision = results.get('decision')
        scores = {
            "CORE": scores[0],
            "Non-CORE": scores[1],
            "Rejected": scores[2],
        }
        # Generate a normalized relevance_score useful for sorting
        # We assume a CORE paper to have the highest relevance so we add a
        # significant value to seperate it from Non-Core and Rejected.
        # Normally scores range from -2 / +2 so 10 is significant.
        # Non-CORE scores are untouched, while Rejected is substracted -10.
        # Finally this provides one normalized score of relevance across
        # all categories of papers.
        relevance_score = max_score
        if decision == "CORE":
            relevance_score += 10
        elif decision == "Rejected":
            relevance_score = (max_score * -1) - 10
        # FIXME: Add top_words info when available from the API
        obj.extra_data["relevance_prediction"] = dict(
            max_score=max_score,
            decision=decision,
            scores=scores,
            relevance_score=relevance_score
        )
        current_app.logger.info("Prediction results: {0}".format(
            obj.extra_data["relevance_prediction"])
        )
