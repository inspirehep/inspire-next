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

"""Set of tasks for classification."""

from __future__ import absolute_import, division, print_function

from flask import current_app
from functools import wraps

from inspire_utils.record import get_value
from inspirehep.modules.workflows.utils import json_api_request
from invenio_classifier import (
    get_keywords_from_local_file,
    get_keywords_from_text,
)
from invenio_classifier.errors import ClassifierException
from invenio_classifier.reader import KeywordToken

from ..proxies import antihep_keywords
from ..utils import with_debug_logging, get_document_in_workflow


CLASSIFIER_MAPPING = {
    "core": "CORE",
    "non_core": "Non-CORE",
    "rejected": "Rejected"
}


def get_classifier_url():
    """Return the classifier URL endpoint, if any."""
    base_url = current_app.config.get('CLASSIFIER_API_URL')
    if not base_url:
        return None

    return '{base_url}/predict/coreness'.format(base_url=base_url)


def prepare_payload(record):
    """Prepare payload to send to Inspire Classifier."""
    payload = {
        'title': get_value(record, 'titles.title[0]', ''),
        'abstract': get_value(record, 'abstracts.value[0]', ''),
    }
    return payload


@with_debug_logging
def guess_coreness(obj, eng):
    """Workflow task to ask inspire classifier for a coreness assessment."""
    predictor_url = get_classifier_url()
    if not predictor_url:
        return

    payload = prepare_payload(obj.data)
    results = json_api_request(predictor_url, payload)

    scores = results["scores"]
    max_score = scores[results['prediction']]
    decision = CLASSIFIER_MAPPING[results["prediction"]]
    scores = {
        "CORE": scores["core"],
        "Non-CORE": scores["non_core"],
        "Rejected": scores["rejected"],
    }
    # Generate a normalized relevance_score useful for sorting
    relevance_score = max_score
    if decision == "CORE":
        relevance_score += 1
    elif decision == "Rejected":
        relevance_score *= -1
    # We assume a CORE paper to have the highest relevance so we add a
    # significant value to seperate it from Non-Core and Rejected.
    # Normally scores range from 0 / +1 so 1 is significant.
    # Non-CORE scores are untouched, while Rejected is set as negative.
    # Finally this provides one normalized score of relevance across
    # all categories of papers.
    obj.extra_data["relevance_prediction"] = dict(
        max_score=max_score,
        decision=decision,
        scores=scores,
        relevance_score=relevance_score
    )
    current_app.logger.info("Prediction results: {0}".format(
        obj.extra_data["relevance_prediction"])
    )


@with_debug_logging
def filter_core_keywords(obj, eng):
    """Filter core keywords."""
    try:
        result = obj.extra_data['classifier_results']["complete_output"]
    except KeyError:
        return
    filtered_core_keywords = [
        keyword for keyword in result.get('core_keywords')
        if keyword['keyword'] not in antihep_keywords
    ]
    result["filtered_core_keywords"] = filtered_core_keywords
    obj.extra_data['classifier_results']["complete_output"] = result


def classify_paper(taxonomy=None, rebuild_cache=False, no_cache=False,
                   output_limit=20, spires=False,
                   match_mode='full', with_author_keywords=False,
                   extract_acronyms=False, only_core_tags=False,
                   fast_mode=False):
    """Extract keywords from a pdf file or metadata in a OAI harvest."""
    @with_debug_logging
    @wraps(classify_paper)
    def _classify_paper(obj, eng):
        from flask import current_app
        params = dict(
            taxonomy_name=taxonomy or current_app.config['HEP_ONTOLOGY_FILE'],
            output_mode='dict',
            output_limit=output_limit,
            spires=spires,
            match_mode=match_mode,
            no_cache=no_cache,
            with_author_keywords=with_author_keywords,
            rebuild_cache=rebuild_cache,
            only_core_tags=only_core_tags,
            extract_acronyms=extract_acronyms
        )

        fulltext_used = True
        with get_document_in_workflow(obj) as tmp_document:
            try:
                if tmp_document:
                    result = get_keywords_from_local_file(tmp_document, **params)
                else:
                    data = get_value(obj.data, 'titles.title', [])
                    data.extend(get_value(obj.data, 'titles.subtitle', []))
                    data.extend(get_value(obj.data, 'abstracts.value', []))
                    data.extend(get_value(obj.data, 'keywords.value', []))
                    if not data:
                        obj.log.error("No classification done due to missing data.")
                        return
                    result = get_keywords_from_text(data, **params)
                    fulltext_used = False
            except ClassifierException as e:
                obj.log.exception(e)
                return

        result['complete_output'] = clean_instances_from_data(
            result.get("complete_output", {})
        )
        result["fulltext_used"] = fulltext_used

        # Check if it is not empty output before adding
        if any(result.get("complete_output", {}).values()):
            obj.extra_data['classifier_results'] = result

    return _classify_paper


def clean_instances_from_data(output):
    """Check if specific keys are of InstanceType and replace them with their id."""
    new_output = {}
    for output_key in output.keys():
        keywords = output[output_key]
        for key in keywords:
            if isinstance(key, KeywordToken):
                keywords[key.id] = keywords.pop(key)
        new_output[output_key] = keywords
    return new_output
