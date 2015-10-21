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

from inspire.utils.helpers import get_record_from_model


def filter_core_keywords(filter_kb):
    """Filter core keywords."""
    @wraps(filter_core_keywords)
    def _filter_core_keywords(obj, eng):
        from inspire.utils.knowledge import check_keys
        from inspire.modules.predicter.utils import (
            get_classification_from_task_results,
            update_classification_in_task_results,
        )

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


def classify_paper(taxonomy, rebuild_cache=False, no_cache=False,
                   output_limit=20, spires=False,
                   match_mode='full', with_author_keywords=False,
                   extract_acronyms=False, only_core_tags=False,
                   fast_mode=False):
    """Extract keywords from a pdf file or metadata in a OAI harvest."""
    from invenio_classifier.api import (
        get_keywords_from_text,
        get_keywords_from_local_file,
    )

    @wraps(classify_paper)
    def _classify_paper(obj, eng):
        from invenio_classifier.errors import TaxonomyError

        model = eng.workflow_definition.model(obj)
        record = get_record_from_model(model)
        data = None
        is_fast_mode = fast_mode
        if not is_fast_mode:
            if "pdf" in obj.extra_data:
                # Getting path to PDF file
                data = obj.extra_data["pdf"]
                callback = get_keywords_from_local_file
        if not data:
            data = [record.get("titles.title", "")].extend(record.get("abstracts.value", []))
            callback = get_keywords_from_text
            is_fast_mode = True

        if not data:
            obj.log.error("No classification done due to missing data.")
            return

        try:
            result = callback(data, taxonomy,
                              output_mode='dict',
                              output_limit=output_limit,
                              spires=spires,
                              match_mode=match_mode,
                              no_cache=no_cache,
                              with_author_keywords=with_author_keywords,
                              rebuild_cache=rebuild_cache,
                              only_core_tags=only_core_tags,
                              extract_acronyms=extract_acronyms)
        except TaxonomyError as e:
            obj.log.exception(e)
            return

        clean_instances_from_data(result.get("complete_output", {}))

        final_result = {"dict": result}
        final_result["fast_mode"] = fast_mode
        # Check if it is not empty output before adding
        output = result.get("complete_output", {}).values()
        if not any(output):
            final_result["dict"] = {}
        name = "classification"
        obj.update_task_results(
            name,
            [{
                "name": name,
                "result": final_result,
                "template": "workflows/results/classifier.html"
            }]
        )

    return _classify_paper


def classify_paper_with_deposit(taxonomy, rebuild_cache=False, no_cache=False,
                                output_limit=20, spires=False,
                                match_mode='full', with_author_keywords=False,
                                extract_acronyms=False, only_core_tags=False,
                                fast_mode=False):
    """Extract keywords from a pdf file or metadata in a deposit."""
    from ..api import (
        get_keywords_from_text,
        get_keywords_from_local_file,
    )

    def _classify_paper_with_deposit(obj, eng):
        from invenio_deposit.models import Deposition
        deposition = Deposition(obj)
        data = None
        if not fast_mode:
            for f in deposition.files:
                if f.name and ".pdf" in f.name.lower():
                    data = f.get_syspath()
                    break
            callback = get_keywords_from_local_file
        if not data:
            try:
                metadata = deposition.get_latest_sip().metadata
            except AttributeError as err:
                obj.log.error("Error getting data: {0}".format(err))

            data = [metadata.get("titles", {}).get("title", ""),
                    metadata.get("abstracts", {}).get("value", "")]
            callback = get_keywords_from_text

        classify_paper(obj, eng, callback, data,
                       taxonomy, rebuild_cache,
                       no_cache, output_limit,
                       spires, match_mode, with_author_keywords,
                       extract_acronyms, only_core_tags, fast_mode)

    return _classify_paper_with_deposit


def clean_instances_from_data(output):
    """Check if specific keys are of InstanceType and replace them with their id."""
    from types import InstanceType

    for output_key in output.keys():
        keywords = output[output_key]
        for key in keywords:
            if type(key) == InstanceType:
                keywords[key.id] = keywords.pop(key)
