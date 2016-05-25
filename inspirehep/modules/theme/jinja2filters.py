# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Jinja utilities for INSPIRE."""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

import json
import re
import datetime
import time

from flask import session, current_app
from jinja2.filters import evalcontextfilter
from inspirehep.utils.jinja2 import render_template_to_string

from inspirehep.utils.date import (
    create_datestruct,
    convert_datestruct_to_dategui,
)
from inspirehep.utils.search import perform_es_search
from inspirehep.utils.template import render_macro_from_template

from .views import blueprint

from inspirehep.modules.records.json_ref_loader import replace_refs

from invenio_search.api import RecordsSearch


def apply_template_on_array(array, template_path, **common_context):
    """Render a template specified by 'template_path'.
    For every item in array, renders the template passing
    the item as 'content' parameter. Additionally ataches
    'common_context' as other rendering arguments.
    Returns list of rendered html strings.
    :param array: iterable with specific context
    :param template_path: path to the template
    :rtype: list of strings
    """

    from collections import Iterable

    rendered = []

    if isinstance(array, basestring):
        array = [array]

    if not isinstance(array, Iterable):
        return rendered

    template = current_app.jinja_env.get_template(template_path)

    for content in array:
        if content:
            rendered.append(
                template.render(content=content, **common_context)
            )

    return rendered


def collection_to_index(collection_name):
    """Translates a collection name to the corresponding index."""
    try:
        mapping = current_app.config['SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING']
        index = mapping[collection_name.lower()]
    except KeyError:
        index = 'records-hep'

    return index


@blueprint.app_template_filter()
@evalcontextfilter
def join_array(eval_ctx, value, separator):
    from jinja2.filters import do_join

    if isinstance(value, basestring):
        value = [value]
    return do_join(eval_ctx, value, separator)


@blueprint.app_template_filter()
def new_line_after(text):
    if not text:
        return text

    return '%s<br>' % text


@blueprint.app_template_filter()
def email_links(value):
    """Return array of links to record emails."""
    return apply_template_on_array(value,
                                   'inspirehep_theme/format/record/field_templates/email.tpl')


@blueprint.app_template_filter()
def url_links(record):
    """
        returns array of links to record emails
    """
    return apply_template_on_array(
        [url["value"] for url in record.get('urls', [])],
        'inspirehep_theme/format/record/field_templates/link.tpl')


@blueprint.app_template_filter()
def institutes_links(record):
    """
        returns array of links to record institutes
    """
    return apply_template_on_array(
        record.get('institute', []),
        'inspirehep_theme/format/record/field_templates/institute.tpl')


@blueprint.app_template_filter()
def author_profile(record):
    """
        returns array of links to record profiles of authores
    """
    return apply_template_on_array(
        record.get('profile', []),
        'inspirehep_theme/format/record/field_templates/author_profile.tpl')


@blueprint.app_template_filter()
def words(value, limit, separator=' '):
    """Return first `limit` number of words ending by `separator`' '"""
    return separator.join(value.split(separator)[:limit])


@blueprint.app_template_filter()
def words_to_end(value, limit, separator=' '):
    """Return last `limit` number of words ending by `separator`' '"""
    return separator.join(value.split(separator)[limit:])


@blueprint.app_template_filter()
def is_list(value):
    """Checks if an object is a list"""
    if isinstance(value, list):
        return True


@blueprint.app_template_filter()
def remove_duplicates(value):
    """Removes duplicate objects from a list and returns the list"""
    if value:
        seen = set()
        uniq = []
        for x in value:
            if x not in seen:
                uniq.append(x)
                seen.add(x)
        return uniq
    return []


@blueprint.app_template_filter()
def has_space(value):
    """Checks if a string contains space"""
    if ' ' in value:
        return True


@blueprint.app_template_filter()
def count_words(value):
    """Counts the amount of words in a string"""
    import re
    from string import punctuation
    words = 0
    if value:
        r = re.compile(r'[{}]'.format(punctuation))
        new_strs = r.sub(' ', value)
        words = len(new_strs.split())
    return words


@blueprint.app_template_filter()
def remove_duplicates_from_dict(value):
    """Actually removed duplicates from a list.

    Kept because other PRs might depend on it.
    FIXME(jacquerie): remove or rename.
    """
    result = []

    for d in value:
        if d not in result:
            result.append(d)

    return result


@blueprint.app_template_filter()
def conference_date(record):
    if 'date' in record and record['date']:
        return record['date']
    from datetime import datetime
    out = ''
    opening_date = record.get('opening_date', '')
    closing_date = record.get('closing_date', '')
    if opening_date and closing_date:
        converted_opening_date = datetime.strptime(
            opening_date, "%Y-%m-%d")
        converted_closing_date = datetime.strptime(
            closing_date, "%Y-%m-%d")
        if opening_date.split('-')[0] == closing_date.split('-')[0]:
            if opening_date.split('-')[1] == closing_date.split('-')[1]:
                out += opening_date.split('-')[2] + '-' + \
                    closing_date.split('-')[2] + \
                    ' ' + converted_opening_date.strftime('%b') + \
                    ' ' + opening_date.split('-')[0]
            else:
                out += opening_date.split('-')[2] + ' ' \
                    + converted_opening_date.strftime('%b') + ' - ' + \
                    closing_date.split('-')[2] + ' ' + \
                    converted_closing_date.strftime('%b') + ' ' + \
                    opening_date.split('-')[0]
        else:
            out += opening_date.split('-')[2] + ' ' + \
                converted_opening_date.strftime('%b') + ' ' \
                + opening_date.split('-')[0] + ' - ' + \
                closing_date.split('-')[2] + ' ' + \
                converted_closing_date.strftime('%b') + ' ' + \
                closing_date.split('-')[0]
    return out


@blueprint.app_template_filter()
def search_for_experiments(value):
    result = ', '.join([
        '<a href="/search?p=experiment_name:%s&cc=Experiments">%s</a>'
        % (i, i) for i in value])
    return result


@blueprint.app_template_filter()
def experiment_date(record):
    result = []
    if 'date_started' in record:
        result.append('Started: ' + record['date_started'])
    if 'date_completed' in record:
        if record.get('date_completed') == '9999':
            result.append('Still Running')
        elif record.get('date_completed'):
            result.append('Completed: ' + record['date_completed'])
    if result:
        return ', '.join(r for r in result)


@blueprint.app_template_filter()
def proceedings_link(record):
    cnum = record.get('cnum', '')
    out = ''
    if not cnum:
        return out

    records = perform_es_search(
        'cnum:%s and 980__a:proceedings' % cnum, 'records-hep')

    if len(records):
        if len(records) > 1:
            proceedings = []

            for i, record in enumerate(records.hits, start=1):
                try:
                    dois = record['dois']
                    proceedings.append(
                        '<a href="/record/{recid}">#{i}</a> (DOI: <a '
                        'href="http://dx.doi.org/{doi}">{doi}</a>'.format(
                            recid=record['control_number'],
                            doi=dois[0]['value'], i=i))
                except KeyError:
                    # Guards both against records not having a "dois" field
                    # and doi values not having a "value" field.
                    proceedings.append(
                        '<a href="/record/{recid}">#{i}</a>'.format(
                            recid=record['control_number'], i=i))

            out = 'Proceedings: '
            out += ', '.join(proceedings)
        else:
            out += '<a href="/record/{recid}">Proceedings</a>'.format(
                recid=records[0]['control_number'])

    return out


@blueprint.app_template_filter()
def experiment_link(record):
    try:
        related_experiments = record['related_experiments']
    except KeyError:
        return []

    result = []
    if related_experiments:
        for element in related_experiments:
            result.append(
                '<a href=/search?cc=Experiments&p=experiment_name:' +
                element['name'] + '>' + element['name'] + '</a>')

    return result


@blueprint.app_template_filter()
def format_cnum_with_slash(value):
    value = str(value)
    cnum = value[:3] + '/' + value[3:5] + '/'
    if "-" in value:
        return value.replace("-", "/")
    else:  # pragma: nocover
        # XXX(jacquerie): never happens.
        if len(value) == 8:
            day = value[5:7]
            nr = value[7]
            return cnum + day + '.' + nr
        else:
            day = value[5:]
            return cnum + day


# XXX(jacquerie): hyphEns.
@blueprint.app_template_filter()
def format_cnum_with_hyphons(value):
    value = str(value)
    cnum = value[:3] + '-' + value[3:5] + '-'
    if "-" in value:
        return value
    else:  # pragma: nocover
        # XXX(jacquerie): never happens.
        if len(value) == 8:
            day = value[5:7]
            nr = value[7]
            return cnum + day + '.' + nr
        else:
            day = value[5:]
            return cnum + day


@blueprint.app_template_filter()
def link_to_hep_affiliation(record):
    try:
        icn = record['ICN']
    except KeyError:
        return ''

    records = perform_es_search('affiliation:%s' % icn, 'records-institutions')
    results = records.hits.total

    if results:
        if results == 1:
            return str(results) + ' Paper from ' + \
                str(record['ICN'])
        else:
            return str(results) + ' Papers from ' + \
                str(record['ICN'])
    else:
        return ''


@blueprint.app_template_filter()
def join_nested_lists(l, sep):
    new_list = [item for sublist in l for item in sublist]
    return sep.join(new_list)


@blueprint.app_template_filter()
def sanitize_collection_name(collection_name):
    """Changes 'hep' to 'literature' and 'hepnames' to 'authors'."""
    if collection_name:
        collection_name = collection_name.strip().lower()

        collection_name = collection_name.replace("hepnames", "authors")
        collection_name = collection_name.replace("hep", "literature")

        return collection_name


@blueprint.app_template_filter()
def collection_select_current(collection_name, current_collection):
    """Returns the active collection based on the current collection page."""
    collection_name = sanitize_collection_name(collection_name)
    current_collection = current_collection.strip().lower()

    if collection_name == current_collection:
        return "active"
    else:
        return ""


@blueprint.app_template_filter()
def number_of_records(collection_name):
    """Returns number of records for the collection."""
    index = collection_to_index(collection_name)
    return perform_es_search('', index).hits.total


@blueprint.app_template_filter()
def sanitize_arxiv_pdf(arxiv_value):
    """Sanitizes the arXiv PDF link so it is always correct"""
    if 'arXiv' in arxiv_value:
        arxiv_value = arxiv_value[6:]

    return arxiv_value + '.pdf'


@blueprint.app_template_filter()
def sort_list_by_dict_val(l):
    from operator import itemgetter
    newlist = sorted(l, key=itemgetter('doc_count'), reverse=True)
    return newlist


@blueprint.app_template_filter()
def epoch_to_year_format(date):
    return time.strftime('%Y', time.gmtime(int(date) / 1000.))


@blueprint.app_template_filter()
def construct_date_format(date):
    starting_date = time.strftime(
        '%Y-%m-%d', time.gmtime(int(date) / 1000.))
    ending_date = time.strftime('%Y-12-31', time.gmtime(int(date) / 1000.))
    return starting_date + '->' + ending_date


@blueprint.app_template_filter()
def limit_facet_elements(l):
    return l[:current_app.config["FACETS_SIZE_LIMIT"]]


@blueprint.app_template_filter()
def author_urls(l, separator):
    result = []
    for name in l:
        if 'name' in name:
            url = '<a href="/search?ln=en&amp;cc=HepNames&amp;p=name:' \
                + name['name'] + '&amp;of=hd">' + name['name'] + '</a>'
            result.append(url)
    return separator.join(result)


@blueprint.app_template_filter()
def ads_links(record):
    lastname = ''
    firstnames = ''
    initial = ''
    link = ''
    author = ''
    amatch = ''
    re_last_first = '^(?P<last>[^,]+)\s*,\s*(?P<first_names>[^\,]*)(?P<extension>\,?.*)$'
    re_initials = r'(?P<initial>\w)([\w`\']+)?.?\s*'
    ADSURL = 'http://adsabs.harvard.edu/cgi-bin/author_form?'
    if 'name' in record:
        author = record['name']['value']
    initialmatch = None
    if author:
        amatch = re.search(re_last_first, author)
    if amatch:
        lastname = amatch.group('last')
        firstnames = amatch.group('first_names')
    if firstnames:
        initialmatch = re.search(re_initials, firstnames)
        firstnames = re.sub('\s+', '+', firstnames)
    if initialmatch:
        initial = initialmatch.group('initial')
    if lastname:
        lastname = re.sub('\s+', '+', lastname)
        link = "%sauthor=%s,+%s&fullauthor=%s,+%s" % \
               (ADSURL, lastname, initial, lastname, firstnames)
    else:
        if 'name' in record:
            # XXX(jacquerie): should escape whitespace?
            link = "%sauthor=%s" % (ADSURL, record['name']['preferred_name'])
    return link


@blueprint.app_template_filter()
def citation_phrase(count):
    if count == 1:
        return 'Cited 1 time'
    else:
        return 'Cited ' + str(count) + ' times'


@blueprint.app_template_filter()
def number_of_search_results(query, collection_name):
    """
    Filter used to show total number of results out of filtered ones.
    """
    session_key = 'last-query' + query + collection_name
    if session.get(session_key):
        query_timestamp = session[session_key]['timestamp']
        seconds_since_query = (
            datetime.datetime.utcnow() - query_timestamp).total_seconds()
        if seconds_since_query < 300:
            # Only use the session value if it is newer than 5 minutes
            # This should allow for the common use case of navigating
            # facets and avoid using an outdated value when using a direct
            # link
            return session[session_key][
                "number_of_hits"
            ]

    index = collection_to_index(collection_name)
    return perform_es_search(query, index).hits.total


@blueprint.app_template_filter()
def is_upper(s):
    return s.isupper()


@blueprint.app_template_filter()
def split_author_name(name):
    new_name = name.split(',')
    return ' '.join(reversed(new_name))


@blueprint.app_template_filter()
def long_timeout(timeout):
    return 5184000  # 60 days


@blueprint.app_template_filter()
def strip_leading_number_plot_caption(text):
    return re.sub(r'^\d{5}\s+', '', text)


@blueprint.app_template_filter()
def json_dumps(data):
    return json.dumps(data)


@blueprint.app_template_filter()
def publication_info(record):
    """Displays inline publication and conference information"""
    result = {}
    out = []
    if 'publication_info' in record:
        journal_title, journal_volume, year, journal_issue, pages = \
            ('', '', '', '', '')
        for pub_info in record['publication_info']:
            if 'journal_title' in pub_info:
                journal_title = '<i>' + pub_info['journal_title'] + '</i>'
                if 'journal_volume' in pub_info:
                    journal_volume = ' ' + pub_info['journal_volume']
                if 'year' in pub_info:
                    year = ' (' + str(pub_info['year']) + ')'
                if 'journal_issue' in pub_info:
                    journal_issue = ' ' + pub_info['journal_issue'] + ', '
                if 'page_artid' in pub_info:
                    pages = ' ' + pub_info['page_artid']
                out.append(journal_title + journal_volume +
                           year + journal_issue + pages)
        if out:
            result['pub_info'] = out
        if not result:
            for field in record['publication_info']:
                if 'pubinfo_freetext' in field:
                    out.append(field['pubinfo_freetext'])
                    result['pub_info'] = out
                    break
        # Conference info line
        for pub_info in record['publication_info']:
            conference_recid = None
            parent_recid = None
            if 'conference_record' in pub_info:
                conference_rec = replace_refs(pub_info['conference_record'],
                                              'es')
                if conference_rec and conference_rec.get('control_number'):
                    conference_recid = conference_rec['control_number']
            if 'parent_record' in pub_info:
                parent_rec = replace_refs(pub_info['parent_record'], 'es')
                parent_recid = parent_rec['control_number']

            if conference_recid and parent_recid:
                try:
                    ctx = {
                        "parent_recid": parent_recid,
                        "conference_recid": conference_recid,
                        "conference_title": conference_rec['title']
                    }
                    if result:
                        result['conf_info'] = render_macro_from_template(
                            name="conf_with_pub_info",
                            template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                            ctx=ctx)
                        break
                    else:
                        if 'page_artid' in pub_info:
                            ctx.update({"page_artid": pub_info['page_artid']})
                        result['conf_info'] = render_macro_from_template(
                            name="conf_without_pub_info",
                            template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                            ctx=ctx)
                        break
                except TypeError:
                    pass
            elif conference_recid and not parent_recid:
                try:
                    ctx = {
                        "conference_recid": conference_recid,
                        "conference_title": conference_rec['title'],
                        "pub_info": bool(result.get('pub_info', ''))
                    }
                    result['conf_info'] = render_macro_from_template(
                        name="conference_only",
                        template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                        ctx=ctx)
                except TypeError:
                    pass
            elif parent_recid and not conference_recid:
                try:
                    ctx = {
                        "parent_recid": parent_recid,
                        "parent_title":
                            parent_rec['titles'][0]['title'].replace(
                                "Proceedings, ", "", 1),
                        "pub_info": bool(result.get('pub_info', ''))
                    }
                    result['conf_info'] = render_macro_from_template(
                        name="proceedings_only",
                        template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                        ctx=ctx)
                except TypeError:
                    pass
    return result


@blueprint.app_template_filter()
def format_date(datetext):
    """Display date in human readable form from available metadata."""
    datestruct = create_datestruct(datetext)

    if datestruct:
        dummy_time = (0, 0, 44, 2, 320, 0)
        if len(datestruct) == 3:
            datestruct = datestruct + dummy_time
            date = convert_datestruct_to_dategui(
                datestruct, output_format="MMM d, Y"
            )
            return date
        elif len(datestruct) == 2:
            datestruct = datestruct + (1,) + dummy_time
            date = convert_datestruct_to_dategui(
                datestruct, output_format="MMM Y"
            )
            return date
        elif len(datestruct) == 1:
            # XXX(jacquerie): returns int instead of string.
            return datestruct[0]


@blueprint.app_template_filter()
def find_collection_from_url(url):
    """Returns the collection based on the URL."""
    if 'cc=conferences' in url or '/conferences' in url:
        return 'conferences'
    elif 'cc=jobs' in url or '/jobs' in url:
        return 'jobs'
    elif 'cc=data' in url or '/data' in url:
        return 'data'
    elif 'cc=institutions' in url or '/institutions' in url:
        return 'institutions'
    elif 'cc=journals' in url or '/journals' in url:
        return 'journals'
    elif 'cc=experiments' in url or '/experiments' in url:
        return 'experiments'
    elif 'cc=authors' in url or '/authors' in url:
        return 'authors'
    return 'literature'


@blueprint.app_template_filter()
def show_citations_number(citation_count):
    """Shows citations number"""
    return 'View all' + str(citation_count) + 'citations'


@blueprint.app_template_filter()
def is_external_link(url):
    """Checks if given url is an external link."""
    return (url.startswith('http') and not url.endswith(
            ('.pdf', '.png', '.jpg', '.jpeg')))


@blueprint.app_template_filter()
def is_institute(institute):
    """Checks if given string is an institute."""
    return institute.lower() in ['kekscan', 'ads', 'cds', 'hal', 'msnet',
                                 'msnet']


@blueprint.app_template_filter()
def get_user_email(id_user):
    """Checks if given string is an institute."""
    from invenio_accounts.models import User
    try:
        email = User.query.get(id_user).email
    except AttributeError:
        email = ''
    return email


@blueprint.app_template_filter()
def weblinks(description):
    """Renames external links based on the description given."""
    value = current_app.extensions.get('inspire-theme').weblinks.get(
        description)
    if value:
        return value.rstrip()
    if description:
        return 'Link to ' + description
    return 'Link to fulltext'


@blueprint.app_template_filter()
def jobs_similar(id):

    out = ''

    es_query = RecordsSearch(index='records-jobs', doc_type='jobs')
    es_query = es_query.query(
        {
            "more_like_this": {
                "docs": [
                    {
                        "_id": id
                    }
                ],
                "min_term_freq": 0,
                "min_doc_freq": 0,
            }
        }
    )[0:2]

    similar_jobs = es_query.execute()

    for job in similar_jobs:
        out = out + (render_template_to_string(
            "inspirehep_theme/similar_jobs.html",
            record=job))

    return out
