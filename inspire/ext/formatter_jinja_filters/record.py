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

from inspire.utils.references import Reference

import time


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


def references(record):
    return Reference(record).references()


def cv_latex(record):
    return Cv_latex(record).format()


def cv_latex_html_text(record, format_type, separator):
    return Cv_latex_html_text(record, format_type, separator).format()


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


def search_for_experiments(value):
    result = ', '.join([
        '<a href="/search?p=experiment_name:%s&cc=Experiments">%s</a>'
        % (i, i)
        for i in value])
    return result


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


def format_cnum_with_slash(value):
    value = str(value)
    cnum = value[:3] + '/' + value[3:5] + '/'
    if "-" in value:
        return value.replace("-", "/")
    else:
        if len(value) == 8:
            day = value[5:7]
            nr = value[7]
            return cnum + day + '.' + nr
        else:
            day = value[5:]
            return cnum + day


def format_cnum_with_hyphons(value):
    value = str(value)
    cnum = value[:3] + '-' + value[3:5] + '-'
    if "-" in value:
        return value
    else:
        if len(value) == 8:
            day = value[5:7]
            nr = value[7]
            return cnum + day + '.' + nr
        else:
            day = value[5:]
            return cnum + day


def link_to_hep_affiliation(record):
    reccnt = Query("affiliation:%s" % (record['department_acronym'],))\
        .search().recids
    if len(reccnt) > 0:
        if len(reccnt) == 1:
            return str(len(reccnt)) + ' Paper from ' +\
                str(record['department_acronym'])
        else:
            return str(len(reccnt)) + ' Papers from ' +\
                str(record['department_acronym'])


def join_nested_lists(l, sep):
    new_list = [item for sublist in l for item in sublist]
    return sep.join(new_list)


def collection_get_title(collection_name):
    if collection_name is None:
        return ""
    collection_name = collection_name.strip().lower()
    if collection_name == "hep":
        return '<i class="fa fa-book"></i> Literature'
    elif collection_name == "hepnames":
        return '<i class="fa fa-users"></i> Authors'
    elif collection_name == "conferences":
        return '<i class="fa fa-calendar"></i> Conferences'
    elif (collection_name == "job" or collection_name == "jobs"):
        return '<i class="fa fa-briefcase"></i> Jobs'
    elif collection_name == "institution" or collection_name == "institutions":
        return '<i class="fa fa-building-o"></i> Institutions'
    elif collection_name == "experiment" or collection_name == "experiments":
        return '<i class="fa fa-flask"></i> Experiments'
    elif collection_name == "journals":
        return 'Journals'
    else:
        return ""


def record_current_collection(collections, current_collection):
    if collections is None:
        return ""
    for collection_name in collections:

        if 'primary' not in collection_name:
            continue

        collection_name = collection_name['primary'].strip().lower()

        if collection_name == "hep" and \
                (current_collection == "Literature" or current_collection == ""):
            return "hep-collection"
        elif collection_name == "hepnames" and \
                (current_collection == "Authors" or current_collection == ""):
            return "hepnames-collection"
        elif collection_name == "conferences" and \
                (current_collection == "Conferences" or current_collection == ""):
            return "conferences-collection"
        elif (collection_name == "jobs" or collection_name == "job") and \
                (current_collection == "Jobs" or current_collection == ""):
            return "jobs-collection"
        elif (collection_name == "institution" or collection_name == "institutions") and \
                (current_collection == "Institutions" or current_collection == ""):
            return "institutions-collection"
        elif collection_name == "experiment" and \
                (current_collection == "Experiments" or current_collection == ""):
            return "experiments-collection"
        elif collection_name == "journals" and \
                (current_collection == "Journals" or current_collection == ""):
            return "journals-collection"

    return ""


def collection_select_current(collection_name, current_collection):
    if collection_name is None:
        return ""
    collection_name = collection_name.strip().lower()
    if collection_name == "hep" and current_collection == "Literature":
        return collection_name + "-collection"
    elif collection_name == "hepnames" and current_collection == "Authors":
        return collection_name + "-collection"
    elif collection_name == "conferences" and \
            current_collection == "Conferences":
        return collection_name + "-collection"
    elif collection_name == "jobs" and current_collection == "Jobs":
        return collection_name + "-collection"
    else:
        return ""


def search_collection(collection_name, is_search):
    if collection_name is None:
        return ""
    collection_name = collection_name.strip().lower()

    if collection_name == "hep":
        search = 'Literature'
    elif collection_name == "hepnames":
        search = 'Authors'
    elif collection_name == "conferences":
        search = 'Conferences'
    elif collection_name == "job" or collection_name == "jobs":
        search = 'Jobs'
    elif collection_name == "institution" or collection_name == "institutions":
        search = 'Institutions'
    elif collection_name == "experiment":
        search = 'Experiments'
    elif collection_name == "journals":
        search = 'Journals'
    else:
        return ""

    if is_search:
        return '&#xF002; Search ' + search
    else:
        return 'Search ' + search + ' >'


def return_collection_name(collections):
    if collections is None:
        return ""
    for collection_name in collections:

        if 'primary' not in collection_name:
            continue

        collection_name = collection_name['primary'].strip().lower()

        if collection_name == "hep" or \
            collection_name == "hepnames" or \
            collection_name == "conferences" or \
                collection_name == "journals":
            return collection_name
        elif (collection_name == "institution" or
                collection_name == "job" or
                collection_name == "experiment"):
            return collection_name + 's'

    return ""


def sanitize_arxiv_pdf(arxiv_value):
    """Sanitizes the arXiv PDF link so it is always correct"""
    if 'arXiv' in arxiv_value:
        arxiv_value = arxiv_value[6:]

    return arxiv_value + '.pdf'


def sort_list_by_dict_val(l):
    from operator import itemgetter
    newlist = sorted(l, key=itemgetter('doc_count'), reverse=True)
    return newlist


def epoch_to_date_format(date):
    return time.strftime('%Y', time.gmtime(int(date) / 1000.))


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
        'search_for_experiments': search_for_experiments,
        'experiment_date': experiment_date,
        'proceedings_link': proceedings_link,
        'experiment_link': experiment_link,
        'format_cnum_with_slash': format_cnum_with_slash,
        'format_cnum_with_hyphons': format_cnum_with_hyphons,
        'link_to_hep_affiliation': link_to_hep_affiliation,
        'join_nested_lists': join_nested_lists,
        'references': references,
        'collection_get_title': collection_get_title,
        'collection_select_current': collection_select_current,
        'search_collection': search_collection,
        'record_current_collection': record_current_collection,
        'return_collection_name': return_collection_name,
        'sanitize_arxiv_pdf': sanitize_arxiv_pdf,
        'epoch_to_date_format': epoch_to_date_format,
        'sort_list_by_dict_val': sort_list_by_dict_val,
    }
