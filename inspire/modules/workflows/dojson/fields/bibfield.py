# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Legacy workflow metadata in BibField conversion to updated data model."""

from __future__ import absolute_import, print_function, unicode_literals

from dojson import utils

from ..model import bibfield


@bibfield.over('abstracts', '^abstract$')
def abstracts(self, key, value):
    """Get abstracts from object."""
    return [{
        'value': value.get('summary'),
        'source': value.get('source')
    }]


@bibfield.over('acquisition_source', '^acquisition_source$')
def acquisition_source(self, key, value):
    """Get acquisition_source from object."""
    return value


@bibfield.over('fft', '^fft$')
def fft(self, key, value):
    """Get FFT from object."""
    return value


@bibfield.over('collections', '^collections$')
def collections(self, key, value):
    """Get collections from object."""
    return value


@bibfield.over('arxiv_eprints', '^system_number_external$')
def arxiv_eprints(self, key, value):
    """Get arxiv_eprints from object."""
    if isinstance(value, dict):
        value = [value]
    for val in value:
        if val.get('institute') == "arXiv":
            return [{'value': val.get('value')}]


@bibfield.over('external_system_numbers', '^system_number_external$')
def external_system_numbers(self, key, value):
    """Get system_number_external from object."""
    if isinstance(value, list):
        return value
    return [value]


@bibfield.over('dois', '^doi$')
def dois(self, key, value):
    """Get DOIs from object."""
    return [{
        'value': value,
    }]


@bibfield.over('license', '^license$')
def license(self, key, value):  # noqa
    """Get license from object."""
    return value


@bibfield.over('page_nr', '^page_nr$')
def page_nr(self, key, value):
    """Get number of pages from object."""
    return value


@bibfield.over('references', '^reference$')
@utils.for_each_value
def references(self, key, value):
    """Get references from object."""
    return value


@bibfield.over('edition', '^edition$')
def edition(self, key, value):
    """Get edition from object."""
    return value


@bibfield.over('refextract', '^refextract$')
def refextract(self, key, value):
    """Get refextract from object."""
    return value


@bibfield.over('report_numbers', '^report_number$')
@utils.for_each_value
def report_numbers(self, key, value):
    """Get report numbers from object."""
    return {
        "value": value.get('primary'),
        "source": value.get('source')
    }


@bibfield.over('subject_terms', '^subject_term$')
def subject_terms(self, key, value):
    """Get subjects from object."""
    return value


@bibfield.over('document_type', '^type_of_doc$')
def document_type(self, key, value):
    """Get subjects from object."""
    return utils.force_list(value)


@bibfield.over('authors', '^authors$', '^_additional_authors$', '^_first_author$')
def authors(self, key, value):
    """Get authors from object."""
    authors = self.get('authors', [])
    value = utils.force_list(value)
    for val in value:
        affiliations = []
        if val.get('affiliation'):
            affiliations = list(set(utils.force_list(
                val.get('affiliation'))))
            affiliations = [{'value': aff} for aff in affiliations]
        authors.append({
            'full_name': val.get('full_name'),
            'role': val.get('relator_term'),
            'alternative_name': val.get('alternative_name'),
            'inspire_id': val.get('INSPIRE_id'),
            'orcid': val.get('external_id'),
            'email': val.get('e_mail'),
            'affiliations': affiliations,
        })
    return authors


@bibfield.over('titles', '^title$')
def titles(self, key, value):
    """Get titles from object."""
    def get_value(existing):
        if not isinstance(value, list):
            values = [value]
        else:
            values = value
        out = []
        for val in values:
            out.append({
                'title': val.get('title'),
                'subtitle': val.get('subtitle'),
                'source': val.get('source'),
            })
        return existing + out

    if 'titles' in self:
        return get_value(self['titles'])
    else:
        return get_value([])


@bibfield.over('breadcrumb_title', '^title$')
def breadcrumb_title(self, key, value):
    """Title used in breadcrum and html title."""
    if isinstance(value, list):
        val = value[0]
    else:
        val = value
    return val.get('title')


@bibfield.over('corporate_author', '^corporate_author$')
@utils.for_each_value
def corporate_author(self, key, value):
    """Get corp. author from object."""
    return value


@bibfield.over('collaboration', '^collaboration$')
@utils.for_each_value
def collaboration(self, key, value):
    """Get collaboration from object."""
    return value


@bibfield.over('preprint_date', '^preprint_info$')
def preprint_date(self, key, value):
    """Get preprint date from object."""
    return value.get('date')


@bibfield.over('hidden_notes', '^hidden_note$')
@utils.for_each_value
def hidden_notes(self, key, value):
    """Get hidden notes from object."""
    return {
        "value": value.get('value'),
        "source": value.get('source')
    }


@bibfield.over('public_notes', '^note$')
@utils.for_each_value
def public_notes(self, key, value):
    """Get public notes from object."""
    return value


@bibfield.over('imprints', '^imprint$')
@utils.for_each_value
def imprints(self, key, value):
    """Get imprints from object."""
    return value


@bibfield.over('oai_pmh', '^oai_pmh$')
def oai_pmh(self, key, value):
    """Get OAI PMH from object."""
    return value


@bibfield.over('thesis', '^thesis$')
def thesis(self, key, value):
    """Get thesis from object."""
    thesis = self.get('thesis', {})
    thesis.update(value)
    return thesis


@bibfield.over('thesis', '^defense_date$')
def defense_date_thesis(self, key, value):
    """Get thesis from object."""
    thesis = self.get('thesis', {})
    thesis.update({"defense_date": value})
    return thesis


@bibfield.over('isbns', '^isbn$')
@utils.for_each_value
@utils.filter_values
def isbns(self, key, value):
    """Get ISBNs from object."""
    return {
        "value": value.get('isbn') or value.get('value'),
        "medium": value.get('medium')
    }


@bibfield.over('copyright', '^coyright$')
def copyright(self, key, value):
    """Get copyright from object."""
    return value


@bibfield.over('accelerator_experiments', '^accelerator_experiment$')
def accelerator_experiments(self, key, value):
    """Get accelerator and experiment from object."""
    if not isinstance(value, list):
        return [value]
    return value


@bibfield.over('language', '^language$')
def language(self, key, value):
    """Get language from object."""
    return value


@bibfield.over('thesis_supervisor', '^thesis_supervisor$')
def thesis_supervisor(self, key, value):
    """Get thesis supervisor from object."""
    if not isinstance(value, list):
        value = [value]
    out = []
    for val in value:
        out.append({
            "full_name": val.get('full_name'),
            "recid": val.get('external_id'),
            "affiliation": {
                "value": val.get('affiliation')
            },
        })
    return out


@bibfield.over('title_translation', '^title_translation$')
@utils.for_each_value
def title_translation(self, key, value):
    """Get translated title from object."""
    return {
        "title": value.get('value'),
        "subtitle": value.get('subtitle'),
    }


@bibfield.over('titles', '^title_arXiv$')
def title_arxiv(self, key, value):
    """Get arXiv title from object."""
    def get_value(existing):
        if not isinstance(value, list):
            values = [value]
        else:
            values = value
        out = []
        for val in values:
            out.append({
                'title': val.get('title'),
                'subtitle': val.get('subtitle'),
                'source': val.get('source'),
            })
        return existing + out

    if 'titles' in self:
        return get_value(self['titles'])
    else:
        return get_value([])


@bibfield.over('spires_sysnos', '^spires_sysno$')
def spires_sysnos(self, key, value):
    """Get SPIRES number from object."""
    if not isinstance(value, list):
        value = [value]
    return [v.get('value') for v in value]


@bibfield.over('url', '^url$')
@utils.for_each_value
def url(self, key, value):
    """Get URLs from object."""
    return value


@bibfield.over('titles_old', '^title_old$')
@utils.for_each_value
def titles_old(self, key, value):
    """Get old titles from object."""
    return {
        'title': value.get('main'),
        'subtitle': value.get('subtitle')
    }


@bibfield.over('publication_info', '^publication_info$')
@utils.for_each_value
def publication_info(self, key, value):
    """Get pubinfo from object."""
    return value


@bibfield.over('free_keywords', '^free_keyword$')
@utils.for_each_value
def free_keywords(self, key, value):
    """Get keywords from object."""
    return value


@bibfield.over('thesaurus_terms', '^thesaurus_terms$')
@utils.for_each_value
def thesaurus_terms(self, key, value):
    """Get thesaurus terms from object."""
    return {
        "keyword": value.get('keyword'),
        "energy_range": value.get('energy_range'),
        "scheme": value.get('classification_scheme')
    }
