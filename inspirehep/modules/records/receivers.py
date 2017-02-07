# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Record receivers."""

from __future__ import absolute_import, division, print_function

from itertools import chain

import six
from flask import current_app
from flask_sqlalchemy import models_committed

from invenio_indexer.api import RecordIndexer
from invenio_indexer.signals import before_record_index
from invenio_records.models import RecordMetadata

from inspirehep.dojson.utils import get_recid_from_ref
from inspirehep.modules.records.api import InspireRecord
from inspirehep.utils.date import create_earliest_date, create_valid_date
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_value

from .experiments import EXPERIMENTS_MAP
from .signals import after_record_enhanced


@models_committed.connect
def receive_after_model_commit(sender, changes):
    """Perform actions after models committed to database."""
    indexer = RecordIndexer()
    for model_instance, change in changes:
        if isinstance(model_instance, RecordMetadata):
            if change in ('insert', 'update'):
                indexer.index(InspireRecord(model_instance.json, model_instance))
            else:
                indexer.delete(InspireRecord(model_instance.json, model_instance))


@before_record_index.connect
def enhance_record(sender, json, *args, **kwargs):
    """Runs all the record enhancers and fires the after_record_enhanced signals
       to allow receivers work with a fully populated record."""
    populate_inspire_subjects(sender, json, *args, **kwargs)
    populate_inspire_document_type(sender, json, *args, **kwargs)
    match_valid_experiments(sender, json, *args, **kwargs)
    dates_validator(sender, json, *args, **kwargs)
    add_recids_and_validate(sender, json, *args, **kwargs)
    populate_experiment_suggest(sender, json, *args, **kwargs)
    populate_abstract_source_suggest(sender, json, *args, **kwargs)
    after_record_enhanced.send(json)


def populate_inspire_subjects(sender, json, *args, **kwargs):
    """Populate the INSPIRE subjects before indexing.

    Adds the `facet_inspire_subjects` key to the record, to be used for
    faceting in the search interface.
    """
    json['facet_inspire_subjects'] = get_value(json, 'inspire_categories.term')


def populate_inspire_document_type(sender, json, *args, **kwargs):
    """Populate the INSPIRE doc type before indexing.

    Adds the ``facet_inspire_doc_type`` key to the record, to be used for
    faceting in the search interface.
    """
    result = []

    result.extend(json.get('document_type', []))
    result.extend(json.get('publication_type', []))
    if 'refereed' in json and json['refereed']:
        result.append('peer reviewed')

    json['facet_inspire_doc_type'] = result


def match_valid_experiments(sender, json, *args, **kwargs):
    """Normalize the experiment names before indexing.

    FIXME: this is currently using a static Python dictionary, while it should
    use the current dynamic state of the Experiments collection.
    """
    def _normalize(experiment):
        try:
            result = EXPERIMENTS_MAP[experiment.lower().replace(' ', '')]
        except KeyError:
            result = experiment

        return result

    if 'accelerator_experiments' in json:
        accelerator_exps = json['accelerator_experiments']
        for accelerator_exp in accelerator_exps:
            facet_experiment = []
            if 'experiment' in accelerator_exp:
                experiments = force_force_list(accelerator_exp['experiment'])
                for experiment in experiments:
                    normalized_experiment = _normalize(experiment)
                    facet_experiment.append(normalized_experiment)
                accelerator_exp['facet_experiment'] = [facet_experiment]


def dates_validator(sender, json, *args, **kwargs):
    """Validate some dates in a record before indexing.

    Logs a warning if the value of a `date_key` in `DATE_KEYS_TO_CHECK` is
    invalid, as determined by the `create_valid_date` function. The valid
    value is substituted for the old value in all cases.
    """
    DATE_KEYS_TO_CHECK = [
        'opening_date',
        'closing_date',
        'deadline_date',
    ]

    for date_key in DATE_KEYS_TO_CHECK:
        if date_key in json:
            valid_date = create_valid_date(json[date_key])
            if valid_date != json[date_key]:
                current_app.logger.warning(
                    'MALFORMED: %s value in %s: %s', date_key,
                    json['control_number'], json[date_key])
            json[date_key] = valid_date


def references_validator(sender, json, *args, **kwargs):
    """Validate the recids in references before indexing.

    Logs a warning if the value corresponding to a `recid` key in `references`
    is not composed uniquely of digits. If it wasn't, it is also removed from
    its reference.
    """
    def _is_not_made_of_digits(recid):
        return not six.text_type(recid).isdigit()

    for reference in json.get('references', []):
        recid = reference.get('recid')
        if recid and _is_not_made_of_digits(recid):
            current_app.logger.warning(
                'MALFORMED: recid value found in references of %s: %s',
                json['control_number'], recid)
            del reference['recid']


def populate_recid_from_ref(sender, json, *args, **kwargs):
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


def add_recids_and_validate(sender, json, *args, **kwargs):
    """Ensure that recids are generated before being validated."""
    populate_recid_from_ref(sender, json, *args, **kwargs)
    references_validator(sender, json, *args, **kwargs)


def populate_experiment_suggest(sender, json, *args, **kwargs):
    """Populates experiment_suggest field of experiment records."""

    # FIXME: Use a dedicated method when #1355 will be resolved.
    if 'experiments.json' in json.get('$schema'):
        experiment_names = get_value(json, 'experiment_names.title')
        title_variants = force_force_list(
            get_value(json, 'title_variants.title'))

        json.update({
            'experiment_suggest': {
                'input': experiment_names + title_variants,
                'output': experiment_names[0],
                'payload': {'$ref': get_value(json, 'self.$ref')},
            },
        })


def populate_abstract_source_suggest(sender, json, *args, **kwargs):
    """Populate abstract_source_suggest field of HEP records."""

    # FIXME: Use a dedicated method when #1355 will be resolved.
    if 'hep.json' in json.get('$schema'):
        abstracts = json.get('abstracts', [])
        for abstract in abstracts:
            source = abstract.get('source')
            if source:
                abstract.update({
                    'abstract_source_suggest': {
                        'input': source,
                        'output': source,
                    },
                })


@before_record_index.connect
def earliest_date(sender, json, *args, **kwargs):
    """Find and assign the earliest date to a HEP paper."""
    date_paths = [
        'preprint_date',
        'thesis.date',
        'thesis.defense_date',
        'publication_info.year',
        'legacy_creation_date',
        'imprints.date',
    ]

    dates = list(chain.from_iterable(
        [force_force_list(get_value(json, path)) for path in date_paths]))

    earliest_date = create_earliest_date(dates)
    if earliest_date:
        json['earliest_date'] = earliest_date
