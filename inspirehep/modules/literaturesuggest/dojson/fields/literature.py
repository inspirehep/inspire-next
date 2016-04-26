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

"""
Literature suggestion form JSON conversion.


Converts keys in the user form to the keys needed by the HEP data model
in order to produce MARCXML.

"""

from ..model import literature

from dojson import utils


@literature.over('abstracts', '^abstract$')
def abstracts(self, key, value):
    return [{
        'value': value,
    }]


@literature.over('_arxiv_id', '^arxiv_id$')
def arxiv_id(self, key, value):
    from idutils import is_arxiv_post_2007

    if is_arxiv_post_2007(value):
        arxiv_rep_number = {'value': 'arXiv:' + value}
    else:
        arxiv_rep_number = {'value': value}
    if len(value.split('/')) == 2:
        arxiv_rep_number['categories'] = value.split('/')[0]
    if 'arxiv_eprints' in self:
        self['arxiv_eprints'].append(arxiv_rep_number)
    else:
        self['arxiv_eprints'] = [arxiv_rep_number]


@literature.over('dois', '^doi$')
def dois(self, key, value):
    return [{
        'value': value,
    }]


@literature.over('authors', '^authors$')
def authors(self, key, value):
    import re

    def match_authors_initials(author_name):
        """Check if author's name contains only its initials."""
        return not bool(re.compile(r'[^A-Z. ]').search(author_name))

    value = filter(None, value)
    for author in value:
        name = author.get('full_name').split(',')
        if len(name) > 1 and \
                match_authors_initials(name[1]):
            name[1] = name[1].replace(' ', '')
            author['full_name'] = ", ".join(name)
        if author.get('affiliation'):
            author['affiliations'] = [dict(value=author['affiliation'])]
            del author['affiliation']
    return value


@literature.over('_categories', '^categories$')
def categories(self, key, value):
    subject_list = [{
        "term": c,
        "scheme": "arXiv"
    } for c in value.split()]
    if 'subject_terms' in self:
        self['subject_terms'].extend(subject_list)
    else:
        self['subject_terms'] = subject_list
    if 'arxiv_eprints' in self:
        self['arxiv_eprints'][0]['categories'] = value.split()
    return value


@literature.over('collaboration', '^collaboration$')
def collaboration(self, key, value):
    return value


@literature.over('hidden_notes', '^hidden_note$')
def hidden_notes(self, key, value):
    return [{
        "value": value
    }]


@literature.over('_conference_id', '^conference_id$')
def conference_id(self, key, value):
    if 'publication_info' in self:
        self['publication_info']['cnum'] = value
    else:
        self['publication_info'] = dict(cnum=value)


@literature.over('_preprint_created', '^preprint_created$')
def preprint_created(self, key, value):
    if 'imprints' in self:
        self['imprints'][0]['date'] = value
    else:
        self['imprints'] = [dict(date=value)]


@literature.over('_defense_date', '^defense_date$')
@utils.for_each_value
def defense_date(self, key, value):
    if 'thesis' in self:
        self['thesis']['defense_date'] = value
    else:
        self['thesis'] = dict(defense_date=value)


@literature.over('_degree_type', '^degree_type$')
def degree_type(self, key, value):
    if 'thesis' in self:
        self['thesis']['degree_type'] = value
    else:
        self['thesis'] = dict(degree_type=value)


@literature.over('_institution', '^institution$')
def institution(self, key, value):
    if 'thesis' in self:
        self['thesis']['university'] = value
    else:
        self['thesis'] = dict(university=value)


@literature.over('_thesis_date', '^thesis_date$')
def thesis_date(self, key, value):
    if 'thesis' in self:
        self['thesis']['date'] = value
    else:
        self['thesis'] = dict(date=value)


@literature.over('accelerator_experiments', '^experiment$')
def accelerator_experiments(self, key, value):
    return [{'experiment': value}]


@literature.over('_issue', 'issue')
def issue(self, key, value):
    if 'publication_info' in self:
        self['publication_info']['journal_issue'] = value
    else:
        self['publication_info'] = dict(issue=value)


@literature.over('_journal_title', '^journal_title$')
def journal_title(self, key, value):
    if 'publication_info' in self:
        self['publication_info']['journal_title'] = value
    else:
        self['publication_info'] = dict(journal_title=value)


@literature.over('_volume', '^volume$')
def volume(self, key, value):
    if 'publication_info' in self:
        self['publication_info']['journal_volume'] = value
    else:
        self['publication_info'] = dict(journal_volume=value)


@literature.over('_year', '^year$')
def year(self, key, value):
    if 'publication_info' in self:
        self['publication_info']['year'] = value
    else:
        self['publication_info'] = dict(year=value)


@literature.over('_page_range_article_id', '^page_range_article_id$')
def page_range_article_id(self, key, value):
    if 'publication_info' in self:
        self['publication_info']['page_artid'] = value
    else:
        self['publication_info'] = dict(page_artid=value)


@literature.over('languages', '^language$')
def languages(self, key, value):
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
        return [unicode(dict(languages).get(value))]
    else:
        return []


@literature.over('_license_url', '^license_url$')
def license_url(self, key, value):
    if 'license' in self:
        self['license']['url'] = value
    else:
        self['license'] = dict(url=value)


@literature.over('public_notes', '^note$')
def public_notes(self, key, value):
    return [{
        'value': value,
    }]


@literature.over('_report_numbers', '^report_numbers$')
def report_numbers(self, key, value):
    """Report numbers coming from the user."""
    repnums = []
    for repnum in value:
        repnums.append(dict(value=repnum.get('report_number')))
    if 'report_numbers' in self:
        self['report_numbers'].extend(repnums)
    else:
        self['report_numbers'] = repnums


@literature.over('subject_terms', '^subject_term$')
def subject_terms(self, key, value):
    return [
        {
            "term": t,
            "scheme": "INSPIRE",
            "source": "submitter"
        }
        for t in value]


@literature.over('thesis_supervisor', '^supervisors$')
def thesis_supervisor(self, key, value):
    return value


@literature.over('titles', '^title$')
def titles(self, key, value):
    def get_value(existing):
        if not isinstance(value, list):
            values = [value]
        else:
            values = value
        out = []
        for val in values:
            out.append({
                'title': val,
            })
        return existing + out

    if 'titles' in self:
        return get_value(self['titles'])
    else:
        return get_value([])


@literature.over('title_translation', '^title_translation$')
def title_translation(self, key, value):
    return [{
        "title": value
    }]


@literature.over('_url', '^url$')
def urls(self, key, value):
    self['pdf'] = value
    field = {
        "url": value
    }
    if 'urls' in self:
        self['urls'].append(field)
    else:
        self['urls'] = [field]


@literature.over('additional_url', '^additional_url$')
def additional_url(self, key, value):
    field = {
        "url": value
    }
    if 'urls' in self:
        self['urls'].append(field)
    else:
        self['urls'] = [field]
