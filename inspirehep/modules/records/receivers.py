# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

"""Pre-record receivers."""

from flask import current_app

from inspirehep.dojson.utils import get_recid_from_ref

from inspirehep.utils.date import create_valid_date

from invenio_indexer.signals import before_record_index

import six

from .signals import after_record_enchanced


@before_record_index.connect
def enhance_record(recid, json, *args, **kwargs):
    """Runs all the record enchancers and fires the after_record_enchanced signals
       to allow receivers work with a fully populated record."""
    populate_inspire_subjects(recid, json, *args, **kwargs)
    populate_inspire_document_type(recid, json, *args, **kwargs)
    match_valid_experiments(recid, json, *args, **kwargs)
    dates_validator(recid, json, *args, **kwargs)
    add_recids_and_validate(recid, json, *args, **kwargs)
    after_record_enchanced.send(json)


def populate_inspire_subjects(recid, json, *args, **kwargs):
    """
    Populate a json record before indexing it to elastic.
    Adds a field for faceting INSPIRE subjects
    """
    inspire_subjects = [
        s['term'] for s in json.get('subject_terms', [])
        if s.get('scheme', '') == 'INSPIRE' and s.get('term')
    ]
    json['facet_inspire_subjects'] = inspire_subjects


def populate_inspire_document_type(recid, json, *args, **kwargs):
    """ Populates a json record before indexing it to elastic.
        Adds a field for faceting INSPIRE document type
    """
    inspire_doc_type = []
    if 'collections' in json:
        for element in json.get('collections', []):
            if 'primary' in element and element.get('primary', ''):
                if element['primary'].lower() == 'published':
                    inspire_doc_type.append('peer reviewed')
                    break
                elif element['primary'].lower() == 'thesis':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'book':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'bookchapter':
                    inspire_doc_type.append('book chapter')
                    break
                elif element['primary'].lower() == 'proceedings':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'conferencepaper':
                    inspire_doc_type.append('conference paper')
                    break
                elif element['primary'].lower() == 'note':
                    inspire_doc_type.append('note')
                    break
                elif element['primary'].lower() == 'report':
                    inspire_doc_type.append(element['primary'].lower())
                    break
        complete_pub_info = []
        if not inspire_doc_type:
            for field in json.get('publication_info', []):
                for k, v in field.iteritems():
                    complete_pub_info.append(k)
            if 'page_artid' not in complete_pub_info:
                inspire_doc_type.append('preprint')
        inspire_doc_type.extend([s['primary'].lower() for s in
                                 json.get('collections', []) if 'primary'
                                 in s and s['primary'] is not None and
                                 s['primary'].lower() in
                                 ('review', 'lectures')])
    json['facet_inspire_doc_type'] = inspire_doc_type


def match_valid_experiments(recid, json, *args, **kwargs):
    """Matches misspelled experiment names with valid experiments.
       Tries to match with valid experiments by matching lowercased and
       whitespace-free versions of known experiments.
    """
    experiments = json.get("accelerator_experiments")
    if experiments:
        for exp in experiments:
            # FIXME: These lists are temporary. We should have a list of experiment names
            # that is generated from the current state of our data.
            from .experiment_list import EXPERIMENTS_NAMES as experiments_list_original, experiments_list
            facet_experiments_list = []
            experiments = exp.get("experiment")
            if experiments:
                if type(experiments) is not list:
                    experiments = [experiments]
                for experiment in experiments:
                    experiment = experiment.lower()
                    experiment = experiment.replace(' ', '')
                    try:
                        # Check if normalized form of experiment is in the list of
                        # valid experiments
                        x = experiments_list.index(experiment)
                        facet_experiment = experiments_list_original[x]
                    except ValueError:
                        # If the experiment cannot be matched it is considered valid
                        facet_experiment = exp.get("experiment")
                    facet_experiments_list.append(facet_experiment)
                exp.update({"facet_experiment": [facet_experiments_list]})


def dates_validator(recid, json, *args, **kwargs):
    """Find and assign the correct dates in a record."""
    dates_to_check = ['opening_date', 'closing_date', 'deadline_date']
    for date_key in dates_to_check:
        if date_key in json:
            valid_date = create_valid_date(json[date_key])
            if valid_date != json[date_key]:
                current_app.logger.warning(
                    'MALFORMED: {0} value in {1}: {3}'.format(
                        date_key, recid, json[date_key]
                    )
                )
            json[date_key] = valid_date


def references_validator(recid, json, *args, **kwargs):
    """Find and assign the correct references in a record."""
    for ref in json.get('references', []):
        if ref.get('recid') and not six.text_type(ref.get('recid')).isdigit():
            # Bad recid! Remove.
            current_app.logger.warning('MALFORMED: recid value found in references of {0}: {1}'.format(recid, ref.get('recid')))
            del ref['recid']


def populate_recid_from_ref(recid, json, *args, **kwargs):
    """Extracts recids from all reference fields and adds them to ES.

    For every field that has as a value a reference object to another record,
    add a sibling after extracting the record id. e.g.
        {"record": {"$ref": "http://x/y/2}}
    is transformed to:
        {"record": {"$ref": "http://x/y/2},
         "recid": 2}
    Siblings are renamed using the following scheme:
        Remove "record" occurrences and append _recid without doubling or
        prepending underscores to the original name.

    For every known list of object references add a new list with the
    corresponding recids. e.g.
        {"records": [{"$ref": "http://x/y/1"}, {"$ref": "http://x/y/2"}]}
        is transformed to:
        {"records": [{"$ref": "http://x/y/1"}, {"$ref": "http://x/y/2"}]
         "recids": [1, 2]}
    """
    list_ref_fields_translations = {
        'deleted_records': 'deleted_recids'
    }

    def _recusive_find_refs(json_root):
        if isinstance(json_root, list):
            items = enumerate(json_root)
        elif isinstance(json_root, dict):
            # Note that items have to be generated before altering the dict.
            # In this case, iteritems might break during iteration.
            items = json_root.items()
        else:
            items = []

        for key, value in items:
            if (isinstance(json_root, dict) and isinstance(value, dict) and
                    '$ref' in value):
                # Append '_recid' and remove 'record' from the key name.
                key_basename = key.replace('record', '').rstrip('_')
                new_key = '{}_recid'.format(key_basename).lstrip('_')
                json_root[new_key] = get_recid_from_ref(value)
            elif (isinstance(json_root, dict) and isinstance(value, list) and
                    key in list_ref_fields_translations):
                new_list = [get_recid_from_ref(v) for v in value]
                new_key = list_ref_fields_translations[key]
                json_root[new_key] = new_list
            else:
                _recusive_find_refs(value)

    _recusive_find_refs(json)


def add_recids_and_validate(recid, json, *args, **kwargs):
    """Ensure that recids are generated before being validated."""
    populate_recid_from_ref(recid, json, *args, **kwargs)
    references_validator(recid, json, *args, **kwargs)
