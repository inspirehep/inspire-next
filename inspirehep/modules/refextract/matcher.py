# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

from __future__ import absolute_import, division, print_function

from inspire_dojson.utils import get_record_ref, get_recid_from_ref
from inspire_matcher import match
from inspire_utils.dedupers import dedupe_list
from inspire_utils.record import get_value

from inspirehep.modules.refextract import config


def _add_match_to_reference(reference, matched_recid, es_index):
    """Modifies a reference to include its record id."""
    if es_index == 'records-data':
        reference['record'] = get_record_ref(matched_recid, 'data')
    elif es_index == 'records-hep':
        reference['record'] = get_record_ref(matched_recid, 'literature')


def match_reference_with_config(reference, config, previous_matched_recid=None):
    """Match a reference using inspire-matcher given the config.

    Args:
        reference (dict): the metadata of the reference.
        config (dict): the list of inspire-matcher configurations for queries.
        previous_matched_recid (int): the record id of the last matched
            reference from the list of references.

    Returns:
        dict: the matched reference.
    """
    # XXX: avoid this type casting.
    try:
        reference['reference']['publication_info']['year'] = str(
            reference['reference']['publication_info']['year'])
    except KeyError:
        pass

    matched_recids = [matched_record['_source']['control_number'] for matched_record in match(reference, config)]
    matched_recids = dedupe_list(matched_recids)

    same_as_previous = any(matched_recid == previous_matched_recid for matched_recid in matched_recids)
    if len(matched_recids) == 1:
        _add_match_to_reference(reference, matched_recids[0], config['index'])
    elif same_as_previous:
        _add_match_to_reference(reference, previous_matched_recid, config['index'])

    # XXX: avoid this type casting.
    try:
        reference['reference']['publication_info']['year'] = int(
            reference['reference']['publication_info']['year'])
    except KeyError:
        pass

    return reference


def match_reference(reference, previous_matched_recid=None):
    """Match a reference using inspire-matcher.

    Args:
        reference (dict): the metadata of a reference.
        previous_matched_recid (int): the record id of the last matched
            reference from the list of references.

    Returns:
        dict: the matched reference.
    """
    if reference.get('curated_relation'):
        return reference

    config_unique_identifiers = config.REFERENCE_MATCHER_UNIQUE_IDENTIFIERS_CONFIG
    config_texkey = config.REFERENCE_MATCHER_TEXKEY_CONFIG
    config_default_publication_info = config.REFERENCE_MATCHER_DEFAULT_PUBLICATION_INFO_CONFIG
    config_jcap_and_jhep_publication_info = config.REFERENCE_MATCHER_JHEP_AND_JCAP_PUBLICATION_INFO_CONFIG
    config_data = config.REFERENCE_MATCHER_DATA_CONFIG

    journal_title = get_value(reference, 'reference.publication_info.journal_title')
    config_publication_info = config_jcap_and_jhep_publication_info if \
        journal_title in ['JCAP', 'JHEP'] else config_default_publication_info

    configs = [config_unique_identifiers, config_publication_info, config_texkey, config_data]

    matches = (match_reference_with_config(reference, config, previous_matched_recid) for config in configs)
    matches = (matched_record for matched_record in matches if 'record' in matched_record)
    reference = next(matches, reference)

    return reference


def match_references(references):
    """Match references to their respective records in INSPIRE.

    Args:
        references (list): the list of references.

    Returns:
        list: the matched references.
    """
    matched_references, previous_matched_recid = [], None
    for ref in references:
        ref = match_reference(ref, previous_matched_recid)
        matched_references.append(ref)
        if 'record' in ref:
            previous_matched_recid = get_recid_from_ref(ref['record'])

    return matched_references
