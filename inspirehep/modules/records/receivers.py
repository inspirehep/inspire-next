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

import six

from flask import current_app

from invenio_records.signals import before_record_index

from inspirehep.utils.date import create_valid_date
from inspirehep.utils.formulas import get_all_unicode_formula_tokens_from_text
from invenio_base.globals import cfg


@before_record_index.connect
def populate_formulas(recid, json, *args, **kwargs):
    """
    Extract all useful LaTeX/MathML formulas from title/abstract and add it
    to the facet_formulas facet.
    """
    if not cfg.get("MATHOID_SERVER"):
        return
    formulas = set()
    for title in json.get('titles', []):
        if 'title' in title:
            formulas |= get_all_unicode_formula_tokens_from_text(title['title'])
    for abstract in json.get('abstracts', []):
        if 'value' in abstract:
            formulas |= get_all_unicode_formula_tokens_from_text(abstract['value'])
    # formulas = [formula for formula in formulas if u'→' in formula and u'=' not in formula]
    json['facet_formulas'] = list(formulas)


@before_record_index.connect
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


@before_record_index.connect
def populate_inspire_document_type(recid, json, *args, **kwargs):
    """ Populates a json record before indexing it to elastic.
        Adds a field for faceting INSPIRE document type
    """
    inspire_doc_type = []
    collections = []
    if 'collections' in json:
        for c in json['collections']:
            if 'primary' in c and c.get('primary', ''):
                if isinstance(c['primary'], list):
                    collections.append(', '.join(c['primary']))
                else:
                    collections.append(c['primary'])
        for idx, item in enumerate(collections):
            collections[idx] = item.lower()
        for element in collections:
            if element == 'published':
                inspire_doc_type.append(element)
                break
            elif element == 'thesis':
                inspire_doc_type.append('peer reviewed')
                break
            elif element == 'book':
                inspire_doc_type.append(element)
                break
            elif element == 'bookchapter':
                inspire_doc_type.append('book chapter')
                break
            elif element == 'proceedings':
                inspire_doc_type.append(element)
                break
            elif element == 'conferencepaper':
                inspire_doc_type.append('conference paper')
                break
            elif element == 'note':
                inspire_doc_type.append(element)
                break
            elif element == 'report':
                inspire_doc_type.append(element)
                break
        complete_pub_info = []
        if not inspire_doc_type:
            for field in json.get('publication_info', []):
                for k, v in field.iteritems():
                    complete_pub_info.append(k)
            if 'page_artid' not in complete_pub_info:
                inspire_doc_type.append('preprint')
        inspire_doc_type.extend([s for s in collections
                                 if s is not None and
                                 s in ('review', 'lectures')])
    json['facet_inspire_doc_type'] = inspire_doc_type


@before_record_index.connect
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


@before_record_index.connect
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


@before_record_index.connect
def references_validator(recid, json, *args, **kwargs):
    """Find and assign the correct references in a record."""
    for ref in json.get('references', []):
        if ref.get('recid') and not six.text_type(ref.get('recid')).isdigit():
            # Bad recid! Remove.
            current_app.logger.warning('MALFORMED: recid value found in references of {0}: {1}'.format(recid, ref.get('recid')))
            del ref['recid']
