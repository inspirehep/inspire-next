# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Jinja utilities for INSPIRE."""

from __future__ import absolute_import, division, print_function

import json
import re
import time
from collections import Iterable
from datetime import datetime
from operator import itemgetter

import six
from flask import current_app, url_for
from jinja2.filters import do_join, evalcontextfilter
from werkzeug.urls import url_decode

from inspire_utils.date import format_date as _format_date
from inspire_utils.dedupers import dedupe_list
from inspirehep.modules.records.wrappers import LiteratureRecord
from inspirehep.modules.search import InstitutionsSearch, LiteratureSearch
from inspirehep.utils.jinja2 import render_template_to_string
from inspirehep.utils.template import render_macro_from_template

from .views import blueprint


def apply_template_on_array(array, template_path, **common_context):
    """Render a template specified by 'template_path'.

    For every item in array, renders the template passing
    the item as 'content' parameter. Additionally attaches
    'common_context' as other rendering arguments.

    Returns list of rendered html strings.

    :param array: iterable with specific context
    :param template_path: path to the template
    :rtype: list of strings
    """
    rendered = []

    if isinstance(array, six.string_types):
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


@blueprint.app_template_filter()
@evalcontextfilter
def join_array(eval_ctx, value, separator):
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
    """Return array of rendered links to emails."""
    return apply_template_on_array(
        value, 'inspirehep_theme/format/record/field_templates/email.tpl')


@blueprint.app_template_filter()
def email_link(value):
    """Return single email rendered (mailto)."""
    return render_template_to_string('inspirehep_theme/format/record/field_templates/email.tpl', content=value)


@blueprint.app_template_filter()
def url_links(record):
    """Return array of rendered links."""
    return apply_template_on_array(
        [url["value"] for url in record.get('urls', [])],
        'inspirehep_theme/format/record/field_templates/link.tpl')


@blueprint.app_template_filter()
def institutes_links(record):
    """Return array of rendered links to institutes."""
    return apply_template_on_array(
        record.get('institute', []),
        'inspirehep_theme/format/record/field_templates/institute.tpl')


@blueprint.app_template_filter()
def author_profile(record):
    """Return array of rendered links to authors."""
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
    """Checks if an object is a list."""
    return isinstance(value, list) or None


@blueprint.app_template_filter()
def remove_duplicates_from_list(l):
    return dedupe_list(l)


@blueprint.app_template_filter()
def conference_date(record):
    if 'date' in record and record['date']:
        return record['date']
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
    if 'date_proposed' in record:
        result.append('Proposed: ' + record['date_proposed'])
    if 'date_approved' in record:
        result.append('Approved: ' + record['date_approved'])
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

    records = LiteratureSearch().query_from_iq(
        'cnum:%s and 980__a:proceedings' % cnum
    ).execute()

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

    records = InstitutionsSearch().query_from_iq(
        'affiliation:%s' % icn
    ).execute()
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
def sanitize_arxiv_pdf(arxiv_value):
    """Sanitizes the arXiv PDF link so it is always correct"""
    if 'arXiv' in arxiv_value:
        arxiv_value = arxiv_value[6:]

    return arxiv_value + '.pdf'


@blueprint.app_template_filter()
def sort_list_by_dict_val(l):
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
def is_upper(s):
    return s.isupper()


@blueprint.app_template_filter()
def format_author_name(name):
    return ' '.join(reversed(name.split(',')))


@blueprint.app_template_filter()
def strip_leading_number_plot_caption(text):
    return re.sub(r'^\d{5}\s+', '', text)


@blueprint.app_template_filter()
def count_plots(record):
    return len(
        [url for url in record.get('urls', []) if
            url.get("value").endswith(('.png', '.jpg'))]
    )


@blueprint.app_template_filter()
def json_dumps(data):
    return json.dumps(data)


@blueprint.app_template_filter()
def publication_info(record):
    """Display inline publication and conference information.

    The record is a LiteratureRecord instance
    """
    if not isinstance(record, LiteratureRecord):
        record = LiteratureRecord(record)
    result = {}
    pub_infos = []
    if 'publication_info' in record:
        for pub_info in record.publication_information:
            pub_info_html = render_macro_from_template(
                name="pub_info",
                template="inspirehep_theme/format/record/Publication_info.tpl",
                ctx=pub_info
            )
            if pub_info_html:
                pub_infos.append(pub_info_html)

        if pub_infos:
            result['pub_info'] = pub_infos

        # Conference info line
        for conf_info in record.conference_information:
            if conf_info.get('conference_recid') and conf_info.get('parent_recid'):
                if result:
                    result['conf_info'] = render_macro_from_template(
                        name="conf_with_pub_info",
                        template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                        ctx={
                            'parent_recid': conf_info.get('parent_recid'),
                            'conference_recid': conf_info.get('conference_recid'),
                            'conference_title': conf_info.get('conference_title'),
                        }
                    )
                    break
                else:
                    result['conf_info'] = render_macro_from_template(
                        name="conf_without_pub_info",
                        template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                        ctx={
                            'parent_recid': conf_info.get('parent_recid'),
                            'conference_recid': conf_info.get('conference_recid'),
                            'conference_title': conf_info.get('conference_title'),
                            'page_start': conf_info.get('page_start'),
                            'page_end': conf_info.get('page_end'),
                            'artid': conf_info.get('artid'),
                        }
                    )
                    break
            elif conf_info.get('conference_recid') and not conf_info.get('parent_recid'):
                result['conf_info'] = render_macro_from_template(
                    name="conference_only",
                    template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                    ctx={
                        'conference_recid': conf_info.get('conference_recid'),
                        'conference_title': conf_info.get('conference_title'),
                        'pub_info': bool(result.get('pub_info')),
                    }
                )
            elif conf_info.get('parent_recid') and not conf_info.get('conference_recid'):
                result['conf_info'] = render_macro_from_template(
                    name="proceedings_only",
                    template="inspirehep_theme/format/record/Conference_info_macros.tpl",
                    ctx={
                        'parent_recid': conf_info.get('parent_recid'),
                        'parent_title': conf_info.get('parent_title'),
                        'pub_info': bool(result.get('pub_info')),
                    }
                )

    return result


@blueprint.app_template_filter()
def format_date(date):
    """Displays a date in a human-friendly format."""
    if date is None:
        return

    return _format_date(date)


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
def back_to_search_link(referer, collection):
    """Creates link to go back to search results in detailed pages."""

    url_map = url_decode(referer)
    text = "Back to {} search results".format(collection.capitalize())
    url = url_for('inspirehep_search.search', cc=collection)
    if referer and url_map.get('q'):
        url = url_for(
            'inspirehep_search.search', cc=collection, q=url_map['q']
        )
        text = u"Back to search results for \"{}\"".format(url_map['q'])
    url_html = u'<a href="{}">{}</a>'.format(url, text)
    return url_html


@blueprint.app_template_filter()
def clean_roles(roles):
    """Extract names from user roles."""
    return json.dumps([role.name for role in roles])


@blueprint.app_template_filter()
def is_cataloger(user):
    """Check if user has a cataloger role."""
    role_names = [role.name for role in user.roles]
    return any(role in role_names for role in ('cataloger', 'superuser'))
