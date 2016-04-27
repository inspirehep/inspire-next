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

"""Set of tasks for classification."""

from functools import wraps

from ..proxies import antihep_keywords


def filter_core_keywords(obj, eng):
    """Filter core keywords."""
    result = obj.extra_data.get('classifier_results').get("complete_output")
    if result is None:
        return
    filtered_core_keywords = {}
    for core_keyword, times_counted in result.get("Core keywords").items():
        if core_keyword not in antihep_keywords:
            filtered_core_keywords[core_keyword] = times_counted
    result["Filtered Core keywords"] = filtered_core_keywords
    obj.extra_data['classifier_results']["complete_output"] = result


def classify_paper(taxonomy, rebuild_cache=False, no_cache=False,
                   output_limit=20, spires=False,
                   match_mode='full', with_author_keywords=False,
                   extract_acronyms=False, only_core_tags=False,
                   fast_mode=False):
    """Extract keywords from a pdf file or metadata in a OAI harvest."""
    @wraps(classify_paper)
    def _classify_paper(obj, eng):
        from invenio_classifier.errors import ClassifierException
        from invenio_classifier import (
            get_keywords_from_text,
            get_keywords_from_local_file,
        )

        params = dict(
            taxonomy_name=taxonomy,
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

        fast_mode = False
        try:
            # FIXME: May need to find another canonical way of getting PDF
            if "pdf" in obj.extra_data:
                result = get_keywords_from_local_file(
                    obj.extra_data["pdf"], **params
                )
            else:
                data = []
                titles = obj.data.get('titles')
                if titles:
                    data.extend([t.get('title', '') for t in titles])
                abstracts = obj.data.get('abstracts')
                if abstracts:
                    data.extend([t.get('value', '') for t in abstracts])
                if not data:
                    obj.log.error("No classification done due to missing data.")
                    return
                result = get_keywords_from_text(data, **params)
                fast_mode = True
        except ClassifierException as e:
            obj.log.exception(e)
            return

        clean_instances_from_data(result.get("complete_output", {}))
        result["fast_mode"] = fast_mode

        # Check if it is not empty output before adding
        if any(result.get("complete_output", {}).values()):
            obj.extra_data['classifier_results'] = result

    return _classify_paper


def clean_instances_from_data(output):
    """Check if specific keys are of InstanceType and replace them with their id."""
    from types import InstanceType

    for output_key in output.keys():
        keywords = output[output_key]
        for key in keywords:
            if type(key) == InstanceType:
                keywords[key.id] = keywords.pop(key)
