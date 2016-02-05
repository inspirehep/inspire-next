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

from invenio_records.signals import before_record_index
from inspirehep.utils.formulas import get_all_unicode_formula_tokens_from_text


@before_record_index.connect
def populate_formulas(recid, json, *args, **kwargs):
    """
    Extract all useful LaTeX/MathML formulas from title/abstract and add it
    to the facet_formulas facet.
    """
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
    if 'collections' in json:
        for element in json.get('collections', []):
            if 'primary' in element and element.get('primary', ''):
                if element['primary'].lower() == 'published':
                    inspire_doc_type.append(element['primary'].lower())
                    break
                elif element['primary'].lower() == 'thesis':
                    inspire_doc_type.append('peer reviewed')
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
