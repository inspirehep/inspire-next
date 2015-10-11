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

from ..model import bibfield

from dojson import utils


@bibfield.over('abstracts', '^abstract$')
def abstracts(self, key, value):
    return [{
        'value': value.get('summary'),
        'source': value.get('source')
    }]


@bibfield.over('acquisition_source', '^acquisition_source$')
def acquisition_source(self, key, value):
    return value


@bibfield.over('fft', '^fft$')
def fft(self, key, value):
    return value


@bibfield.over('collections', '^collections$')
def collections(self, key, value):
    return value


@bibfield.over('arxiv_eprints', '^system_number_external$')
def arxiv_eprints(self, key, value):
    if isinstance(value, dict):
        value = [value]
    for val in value:
        if val.get('institute') == "arXiv":
            return [{'value': val.get('value')}]


@bibfield.over('external_system_numbers', '^system_number_external$')
def external_system_numbers(self, key, value):
    if isinstance(value, list):
        return value
    return [value]


@bibfield.over('dois', '^doi$')
def dois(self, key, value):
    return [{
        'value': value,
    }]


@bibfield.over('license', '^license$')
def license(self, key, value):  # noqa
    return value


@bibfield.over('page_nr', '^page_nr$')
def page_nr(self, key, value):
    return value


@bibfield.over('references', '^reference$')
@utils.for_each_value
def references(self, key, value):
    return value


@bibfield.over('edition', '^edition$')
def edition(self, key, value):
    return value


@bibfield.over('refextract', '^refextract$')
def refextract(self, key, value):
    return value


@bibfield.over('report_numbers', '^report_number$')
@utils.for_each_value
def report_numbers(self, key, value):
    """Report numbers."""
    return {
        "value": value.get('primary'),
        "source": value.get('source')
    }


@bibfield.over('subject_terms', '^subject_term$')
def subject_terms(self, key, value):
    return value


@bibfield.over('authors', '^authors$')
@utils.for_each_value
def authors(self, key, value):
    affiliations = []
    if value.get('affiliation'):
        affiliations = list(set(utils.force_list(
            value.get('affiliation'))))
        affiliations = [{'value': aff} for aff in affiliations]
    return {
        'full_name': value.get('full_name'),
        'role': value.get('relator_term'),
        'alternative_name': value.get('alternative_name'),
        'inspire_id': value.get('INSPIRE_id'),
        'orcid': value.get('external_id'),
        'email': value.get('e_mail'),
        'affiliations': affiliations,
    }


@bibfield.over('titles', '^title$')
def titles(self, key, value):
    def get_value(existing):
        if not isinstance(value, list):
            values = [value]
        else:
            values = value
        out = []
        for val in values:
            out.append({
                'title': val.get('a'),
                'subtitle': val.get('b'),
                'source': val.get('9'),
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
    return value


@bibfield.over('collaboration', '^collaboration$')
@utils.for_each_value
def collaboration(self, key, value):
    return value


@bibfield.over('preprint_date', '^preprint_info$')
def preprint_date(self, key, value):
    return value.get('date')


@bibfield.over('hidden_notes', '^hidden_note$')
@utils.for_each_value
def hidden_notes(self, key, value):
    return {
        "value": value.get('value'),
        "source": value.get('source')
    }


@bibfield.over('public_notes', '^note$')
@utils.for_each_value
def public_notes(self, key, value):
    return value


@bibfield.over('imprints', '^imprint$')
@utils.for_each_value
def imprints(self, key, value):
    return value


@bibfield.over('oai_pmh', '^oai_pmh$')
@utils.for_each_value
def oai_pmh(self, key, value):
    return value


@bibfield.over('thesis', '^thesis$')
def thesis(self, key, value):
    return value


@bibfield.over('isbns', '^isbn$')
def isbns(self, key, value):
    if not isinstance(value, list):
        return [value]
    return value


@bibfield.over('copyright', '^coyright$')
def copyright(self, key, value):
    return value


@bibfield.over('accelerator_experiments', '^accelerator_experiment$')
def accelerator_experiments(self, key, value):
    if not isinstance(value, list):
        return [value]
    return value


@bibfield.over('language', '^language$')
def language(self, key, value):
    languages = [("en", "English"),
                 ("rus", "Russian"),
                 ("ger", "German"),
                 ("fre", "French"),
                 ("ita", "Italian"),
                 ("spa", "Spanish"),
                 ("chi", "Chinese"),
                 ("por", "Portuguese"),
                 ("oth", "Other")]

    if value not in ('en', 'oth'):
        return unicode(dict(languages).get(value))
    else:
        return value


@bibfield.over('thesis_supervisor', '^thesis_supervisor$')
def thesis_supervisor(self, key, value):
    if not isinstance(value, list):
        return [value]
    return value


@bibfield.over('title_translation', '^title_translation$')
@utils.for_each_value
def title_translation(self, key, value):
    return {
        "title": value.get('value'),
        "subtitle": value.get('subtitle'),
    }


@bibfield.over('titles', '^title_arXiv$')
def title_arxiv(self, key, value):
    def get_value(existing):
        if not isinstance(value, list):
            values = [value]
        else:
            values = value
        out = []
        for val in values:
            out.append({
                'title': val.get('a'),
                'subtitle': val.get('b'),
                'source': val.get('9'),
            })
        return existing + out

    if 'titles' in self:
        return get_value(self['titles'])
    else:
        return get_value([])


@bibfield.over('spires_sysnos', '^spires_sysno$')
def spires_sysnos(self, key, value):
    return [value.get('value')]


@bibfield.over('url', '^url$')
@utils.for_each_value
def url(self, key, value):
    return value


@bibfield.over('titles_old', '^title_old$')
def titles_old(self, key, value):
    if not isinstance(value, list):
        value = [value]
    return [
        {
            'title': val.get('main'),
            'subtitle': val.get('subtitle')
        } for val in value
    ]


@bibfield.over('publication_info', '^publication_info$')
@utils.for_each_value
def publication_info(self, key, value):
    return value


@bibfield.over('free_keywords', '^free_keyword$')
@utils.for_each_value
def free_keywords(self, key, value):
    return value


@bibfield.over('thesaurus_terms', '^thesaurus_terms$')
@utils.for_each_value
def thesaurus_terms(self, key, value):
    return {
        "keyword": value.get('keyword'),
        "energy_range": value.get('energy_range'),
        "scheme": value.get('classification_scheme')
    }
