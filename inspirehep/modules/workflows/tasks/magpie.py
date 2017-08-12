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

"""Set of workflow tasks for MagPie API."""

from __future__ import absolute_import, division, print_function

import requests

from flask import current_app

from inspire_utils.record import get_value
from inspirehep.modules.workflows.utils import json_api_request

from ..utils import with_debug_logging


@with_debug_logging
def get_magpie_url():
    """Return the Magpie URL endpoint, if any."""
    base_url = current_app.config.get("MAGPIE_API_URL")
    if not base_url:
        return
    return "{base_url}/predict".format(
        base_url=base_url
    )


@with_debug_logging
def prepare_magpie_payload(record, corpus):
    """Prepare payload to send to Magpie API."""
    payload = dict(text="", corpus=corpus)
    titles = filter(None, get_value(record, "titles.title", []))
    abstracts = filter(None, get_value(record, "abstracts.value", []))
    payload["text"] = ". ".join(
        [part.encode('utf-8') for part in titles + abstracts])
    return payload


@with_debug_logging
def filter_magpie_response(labels, limit):
    """Filter response from Magpie API, keeping most relevant labels."""
    filtered_labels = [
        (word, score) for word, score in labels
        if score >= limit
    ]

    # In the event that there are no labels with a high enough score,
    # we take only the top one
    if labels and len(filtered_labels) == 0:
        filtered_labels.append(labels[0])
    return filtered_labels


@with_debug_logging
def guess_keywords(obj, eng):
    """Workflow task to ask Magpie API for a keywords assessment."""
    magpie_url = get_magpie_url()
    if not magpie_url:
        # Skip task if no API URL set
        return
    payload = prepare_magpie_payload(obj.data, corpus="keywords")
    try:
        results = json_api_request(magpie_url, payload)
    except requests.exceptions.RequestException:
        results = {}

    if results:
        labels = results.get('labels', [])
        keywords = labels[:10]

        keywords = [{'label': k[0], 'score': k[1], 'accept': k[1] >= 0.09} for
                    k in
                    keywords]
        obj.extra_data["keywords_prediction"] = dict(
            keywords=keywords
        )
        current_app.logger.info("Keyword prediction (top 10): {0}".format(
            obj.extra_data["keywords_prediction"]["keywords"]
        ))


@with_debug_logging
def guess_categories(obj, eng):
    """Workflow task to ask Magpie API for a subject area assessment."""
    magpie_url = get_magpie_url()
    if not magpie_url:
        # Skip task if no API URL set
        return
    payload = prepare_magpie_payload(obj.data, corpus="categories")
    results = json_api_request(magpie_url, payload)
    if results:
        labels = results.get('labels', [])
        categories = filter_magpie_response(labels, limit=0.22)

        categories = [{'label': c[0], 'score': c[1],
                       'accept': c[1] >= 0.25} for c in categories]

        obj.extra_data["categories_prediction"] = dict(
            categories=categories
        )
        current_app.logger.info("Category prediction: {0}".format(
            obj.extra_data["categories_prediction"]["categories"]
        ))


@with_debug_logging
def guess_experiments(obj, eng):
    """Workflow task to ask Magpie API for a subject area assessment."""
    magpie_url = get_magpie_url()
    if not magpie_url:
        # Skip task if no API URL set
        return

    payload = prepare_magpie_payload(obj.data, corpus="experiments")
    results = json_api_request(magpie_url, payload)
    if results:
        all_predictions = results.get('labels', [])
        selected_experiments = filter_magpie_response(
            all_predictions,
            limit=0.5,
        )
        selected_experiments = [
            {'label': e[0], 'score': e[1]}
            for e in selected_experiments
        ]
        obj.extra_data["experiments_prediction"] = dict(
            experiments=selected_experiments,
        )
        current_app.logger.info("Experiment prediction: {0}".format(
            obj.extra_data["experiments_prediction"]["experiments"]
        ))
