# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

from inspire.ext.formatter_jinja_filters.general import apply_template_on_array

from inspire.utils.bibtex import Bibtex
from inspire.utils.latex import Latex
from inspire.utils.cv_latex import Cv_latex
from inspire.utils.cv_latex_html_text import Cv_latex_html_text
from invenio_search.api import Query


def email_links(value):
    """
        returns array of links to record emails
    """
    return apply_template_on_array(value,
                                   'format/record/field_templates/email.tpl')


def url_links(record):
    """
        returns array of links to record emails
    """
    return apply_template_on_array([url["value"] for url in
                                    record.get('urls', [])],
                                   'format/record/field_templates/link.tpl')


def institutes_links(record):
    """
        returns array of links to record institutes
    """
    return apply_template_on_array(record.get('institute', []),
                                   'format/record/field_templates/institute.tpl')


def author_profile(record):
    """
        returns array of links to record profiles of authores
    """
    return apply_template_on_array(record.get('profile', []),
                                   'format/record/field_templates/author_profile.tpl')


def words(value, limit, separator=' '):
    """Return first `limit` number of words ending by `separator`' '"""
    return separator.join(value.split(separator)[:limit])


def words_to_end(value, limit, separator=' '):
    """Return last `limit` number of words ending by `separator`' '"""
    return separator.join(value.split(separator)[limit:])


def is_list(value):
    """Checks if an object is a list"""
    if isinstance(value, list):
        return True


def remove_duplicates(value):
    """Removes duplicate objects from a list and returns the list"""
    seen = set()
    uniq = []
    for x in value:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return uniq


def has_space(value):
    """Checks if a string contains space"""
    if ' ' in value:
        return True


def count_words(value):
    """Counts the amount of words in a string"""
    import re
    from string import punctuation
    r = re.compile(r'[{}]'.format(punctuation))
    new_strs = r.sub(' ', value)
    return len(new_strs.split())


def is_intbit_set(value):
    from intbitset import intbitset
    if isinstance(value, intbitset):
        value = value.tolist()
    return value


def remove_duplicates_from_dict(value):
    return [dict(t) for t in set([tuple(d.items()) for d in value])]


def bibtex(record):
    return Bibtex(record).format()


def latex(record, latex_format):
    return Latex(record, latex_format).format()


def cv_latex(record):
    return Cv_latex(record).format()


def cv_latex_html_text(record, format_type):
    return Cv_latex_html_text(record, format_type).format()


def conference_date(record):
    if 'date' in record and record['date']:
        return record['date']
    from datetime import datetime
    out = ''
    opening_date = record['opening_date']
    closing_date = record['closing_date']
    converted_opening_date = datetime.strptime(opening_date, "%Y-%m-%d")
    converted_closing_date = datetime.strptime(closing_date, "%Y-%m-%d")
    if opening_date.split('-')[0] == closing_date.split('-')[0]:
        if opening_date.split('-')[1] == closing_date.split('-')[1]:
            out += opening_date.split('-')[2] + '-' +\
                closing_date.split('-')[2] +\
                ' ' + converted_opening_date.strftime('%b') +\
                ' ' + opening_date.split('-')[0]
        else:
            out += opening_date.split('-')[2] + ' '\
                + converted_opening_date.strftime('%b') + ' - ' +\
                closing_date.split('-')[2] + ' ' +\
                converted_closing_date.strftime('%b') + ' ' +\
                opening_date.split('-')[0]
    else:
        out += opening_date.split('-')[2] + ' ' +\
            converted_opening_date.strftime('%b') + ' '\
            + opening_date.split('-')[0] + ' - ' + \
            closing_date.split('-')[2] + ' ' +\
            converted_closing_date.strftime('%b') + ' ' +\
            closing_date.split('-')[0]
    return out


def experiment_date(record):
    result = []
    if 'date_started' in record:
        result.append('Started: ' + record['date_started'])
    if 'date_completed' in record:
        if record['date_completed'] == '9999':
            result.append('Still Running')
        else:
            result.append('Completed: ' + record['date_completed'])
    if result:
        return ', '.join(r for r in result)


def proceedings_link(record):
    cnum = record['cnum']
    out = ''
    if not cnum:
        return out
    search_result = Query("cnum:%s and 980__a:proceedings" % (cnum,)).\
        search().recids
    if search_result:
        if len(search_result) > 1:
            from invenio.legacy.bibrecord import get_fieldvalues
            proceedings = []
            for i, recid in enumerate(search_result):
                doi = get_fieldvalues(recid, '0247_a')
                if doi:
                    proceedings.append('<a href="/record/%(ID)s">#%(number)s</a> (DOI: <a href="http://dx.doi.org/%(doi)s">%(doi)s</a>)'
                                       % {'ID': recid, 'number': i + 1, 'doi': doi[0]})
                else:
                    proceedings.append(
                        '<a href="/record/%(ID)s">#%(number)s</a>' % {'ID': recid, 'number': i + 1})
                out = 'Proceedings: '
                out += ', '.join(proceedings)
        elif len(search_result) == 1:
            out += '<a href="/record/' + str(search_result[0]) + \
                '">Proceedings</a>'
    return out


def experiment_link(record):
    result = []
    if record['related_experiments']:
        for element in record['related_experiments']:
            result.append(
                '<a href=/search?cc=Experiments&p=experiment_name:' +
                element['name'] + '>' + element['name'] + '</a>')
    return result


def get_filters():
    return {
        'email_links': email_links,
        'institute_links': institutes_links,
        'author_profile': author_profile,
        'url_links': url_links,
        'words': words,
        'words_to_end': words_to_end,
        'is_list': is_list,
        'remove_duplicates': remove_duplicates,
        'has_space': has_space,
        'count_words': count_words,
        'is_intbit_set': is_intbit_set,
        'remove_duplicates_from_dict': remove_duplicates_from_dict,
        'bibtex': bibtex,
        'latex': latex,
        'cv_latex': cv_latex,
        'cv_latex_html_text': cv_latex_html_text,
        'conference_date': conference_date,
        'experiment_date': experiment_date,
        'proceedings_link': proceedings_link,
        'experiment_link': experiment_link,
    }
