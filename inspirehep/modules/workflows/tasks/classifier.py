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

from functools import wraps

from inspire_utils.record import get_value
from invenio_classifier import (
    get_keywords_from_local_file,
    get_keywords_from_text,
)
from invenio_classifier.errors import ClassifierException
from invenio_classifier.reader import KeywordToken

from ..proxies import antihep_keywords
from ..utils import with_debug_logging, get_document_in_workflow


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
