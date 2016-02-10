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

import re
import datetime
import time

from flask import session

from inspirehep.ext.jinja_filters.general import apply_template_on_array

from inspirehep.utils.bibtex import Bibtex
from inspirehep.utils.cv_latex import Cv_latex
from inspirehep.utils.cv_latex_html_text import Cv_latex_html_text
from inspirehep.utils.latex import Latex

from invenio_ext.es import es
from invenio_ext.template.utils import render_macro_from_template

from invenio_base.globals import cfg

from invenio_search.api import Query


def setup_app(app):
    """Register filters used in record templates. """

    @app.template_filter()
    def email_links(value):
        """Return array of links to record emails."""
        return apply_template_on_array(
            value,
            'format/record/field_templates/email.tpl'
        )

    @app.template_filter()
    def url_links(record):
        """
            returns array of links to record emails
        """
        return apply_template_on_array([url["value"] for url in
                                        record.get('urls', [])],
                                       'format/record/field_templates/link.tpl')

    @app.template_filter()
    def institutes_links(record):
        """
            returns array of links to record institutes
        """
        return apply_template_on_array(record.get('institute', []),
                                       'format/record/field_templates/institute.tpl')

    @app.template_filter()
    def author_profile(record):
        """
            returns array of links to record profiles of authores
        """
        return apply_template_on_array(record.get('profile', []),
                                       'format/record/field_templates/author_profile.tpl')

    @app.template_filter()
    def words(value, limit, separator=' '):
        """Return first `limit` number of words ending by `separator`' '"""
        return separator.join(value.split(separator)[:limit])

    @app.template_filter()
    def words_to_end(value, limit, separator=' '):
        """Return last `limit` number of words ending by `separator`' '"""
        return separator.join(value.split(separator)[limit:])

    @app.template_filter()
    def is_list(value):
        """Checks if an object is a list"""
        if isinstance(value, list):
            return True

    @app.template_filter()
    def remove_duplicates(value):
        """Removes duplicate objects from a list and returns the list"""
        seen = set()
        uniq = []
        for x in value:
            if x not in seen:
                uniq.append(x)
                seen.add(x)
        return uniq

    @app.template_filter()
    def has_space(value):
        """Checks if a string contains space"""
        if ' ' in value:
            return True

    @app.template_filter()
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

    @app.template_filter()
    def is_intbit_set(value):
        from intbitset import intbitset
        if isinstance(value, intbitset):
            value = value.tolist()
        return value

    @app.template_filter()
    def remove_duplicates_from_dict(value):
        return [dict(t) for t in set([tuple(d.items()) for d in value])]

    @app.template_filter()
    def bibtex(record):
        return Bibtex(record).format()

    @app.template_filter()
    def latex(record, latex_format):
        return Latex(record, latex_format).format()

    @app.template_filter()
    def cv_latex(record):
        return Cv_latex(record).format()

    @app.template_filter()
    def cv_latex_html_text(record, format_type, separator):
        return Cv_latex_html_text(record, format_type, separator).format()

    @app.template_filter()
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

    @app.template_filter()
    def search_for_experiments(value):
        result = ', '.join([
            '<a href="/search?p=experiment_name:%s&cc=Experiments">%s</a>'
            % (i, i)
            for i in value])
        return result

    @app.template_filter()
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

    @app.template_filter()
    def proceedings_link(record):
        cnum = record.get('cnum', '')
        out = ''
        if not cnum:
            return out
        search_result = Query("cnum:%s and 980__a:proceedings" % (cnum,)).\
            search()
        if len(search_result):
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
            else:
                out += '<a href="/record/' + str(search_result[0]) + \
                    '">Proceedings</a>'
        return out

    @app.template_filter()
    def experiment_link(record):
        result = []
        if record['related_experiments']:
            for element in record['related_experiments']:
                result.append(
                    '<a href=/search?cc=Experiments&p=experiment_name:' +
                    element['name'] + '>' + element['name'] + '</a>')
        return result

    @app.template_filter()
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

    @app.template_filter()
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

    @app.template_filter()
    def link_to_hep_affiliation(record):
        reccnt = Query("affiliation:%s" % (record['ICN'],))\
            .search()
        if len(reccnt):
            if len(reccnt) == 1:
                return str(len(reccnt)) + ' Paper from ' +\
                    str(record['ICN'])
            else:
                return str(len(reccnt)) + ' Papers from ' +\
                    str(record['ICN'])

    @app.template_filter()
    def join_nested_lists(l, sep):
        new_list = [item for sublist in l for item in sublist]
        return sep.join(new_list)

    @app.template_filter()
    def sanitize_collection_name(collection_name):
        """Changes 'hep' to 'literature' and 'hepnames' to 'authors'."""
        if collection_name:
            collection_name = collection_name.strip().lower()

            collection_name = collection_name.replace("hepnames", "authors")
            collection_name = collection_name.replace("hep", "literature")

            return collection_name

    @app.template_filter()
    def collection_select_current(collection_name, current_collection):
        """Returns the active collection based on the current collection page."""

        collection_name = sanitize_collection_name(collection_name)
        current_collection = current_collection.strip().lower()

        if collection_name == current_collection:
            return "active"
        else:
            return ""

    @app.template_filter()
    def number_of_records(collection_name):
        """Returns number of records for the collection."""
        return len(Query("").
                   search(collection=collection_name))

    @app.template_filter()
    def sanitize_arxiv_pdf(arxiv_value):
        """Sanitizes the arXiv PDF link so it is always correct"""
        if 'arXiv' in arxiv_value:
            arxiv_value = arxiv_value[6:]

        return arxiv_value + '.pdf'

    @app.template_filter()
    def sort_list_by_dict_val(l):
        from operator import itemgetter
        newlist = sorted(l, key=itemgetter('doc_count'), reverse=True)
        return newlist

    @app.template_filter()
    def epoch_to_year_format(date):
        return time.strftime('%Y', time.gmtime(int(date) / 1000.))

    @app.template_filter()
    def construct_date_format(date):
        starting_date = time.strftime(
            '%Y-%m-%d', time.gmtime(int(date) / 1000.))
        ending_date = time.strftime('%Y-12-31', time.gmtime(int(date) / 1000.))
        return starting_date + '->' + ending_date

    @app.template_filter()
    def limit_facet_elements(l):
        return l[:cfg["FACETS_SIZE_LIMIT"]]

    @app.template_filter()
    def author_urls(l, separator):
        result = []
        for name in l:
            if 'name' in name:
                url = '<a href="/search?ln=en&amp;cc=HepNames&amp;p=name:'\
                      + name['name'] + '&amp;of=hd">' + name['name'] + '</a>'
                result.append(url)
        return separator.join(result)

    @app.template_filter()
    def ads_links(record):
        lastname = ''
        firstnames = ''
        initial = ''
        link = ''
        re_last_first = '^(?P<last>[^,]+)\s*,\s*(?P<first_names>[^\,]*)(?P<extension>\,?.*)$'
        re_initials = r'(?P<initial>\w)([\w`\']+)?.?\s*'
        ADSURL = 'http://adsabs.harvard.edu/cgi-bin/author_form?'
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
            link = "%sauthor=%s" % (ADSURL, record['name']['preferred_name'])
        return link

    @app.template_filter()
    def citation_phrase(count):
        if count == 1:
            return 'Cited 1 time'
        else:
            return 'Cited ' + str(count) + ' times'

    @app.template_filter()
    def number_of_search_results(query, collection_name):
        """
        Filter used to show total number of results out of filtered ones.
        """
        session_key = 'last-query' + query + collection_name
        if session.get(session_key):
            query_timestamp = session[session_key]['timestamp']
            seconds_since_query = (datetime.datetime.utcnow() - query_timestamp).total_seconds()
            if seconds_since_query < 300:
                # Only use the session value if it is newer than 5 minutes
                # This should allow for the common use case of navigating
                # facets and avoid using an outdated value when using a direct
                # link
                return session[session_key][
                    "number_of_hits"
                ]
        # Replay the Query to get total number of hits
        return len(Query("%s" % (query,)).
                   search(collection=collection_name))

    @app.template_filter()
    def is_upper(s):
        return s.isupper

    @app.template_filter()
    def split_author_name(name):
        new_name = name.split(',')
        return ' '.join(reversed(new_name))

    @app.template_filter()
    def long_timeout(timeout):
        return 5184000  # 60 days

    @app.template_filter()
    def publication_info(record):
        """Displays inline publication and conference information"""
        result = {}
        out = []
        """Publication info line"""
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
                if 'conference_recid' in pub_info \
                        and 'parent_recid' in pub_info:
                    conference_rec = es.get_source(
                        index='conferences',
                        id=pub_info['conference_recid'],
                        doc_type='record')
                    ctx = {
                        "parent_recid": str(
                            pub_info['parent_recid']),
                        "conference_recid": str(
                            pub_info['conference_recid']),
                        "conference_title": conference_rec['title']
                    }
                    if result:
                        result['conf_info'] = render_macro_from_template(
                            name="conf_with_pub_info",
                            template="format/record/Conference_info_macros.tpl",
                            ctx=ctx)
                        break
                    else:
                        if 'page_artid' in pub_info:
                            ctx.update(
                                {"page_artid": pub_info['page_artid']})
                        result['conf_info'] = render_macro_from_template(
                            name="conf_without_pub_info",
                            template="format/record/Conference_info_macros.tpl",
                            ctx=ctx)
                        break
                elif 'conference_recid' in pub_info \
                        and 'parent_recid' not in pub_info:
                    conference_rec = es.get_source(
                        index='conferences',
                        id=pub_info['conference_recid'],
                        doc_type='record')
                    ctx = {
                        "conference_recid": str(
                            pub_info['conference_recid']),
                        "conference_title": conference_rec['title'],
                        "pub_info": bool(result.get('pub_info', ''))
                    }
                    result['conf_info'] = render_macro_from_template(
                        name="conference_only",
                        template="format/record/Conference_info_macros.tpl",
                        ctx=ctx)
                elif 'parent_recid' in pub_info and \
                        'conference_recid' not in pub_info:
                    parent_rec = es.get_source(
                        index='hep',
                        id=pub_info['parent_recid'],
                        doc_type='record')
                    ctx = {
                        "parent_recid": str(
                            pub_info['parent_recid']),
                        "parent_title": parent_rec['titles'][0]['title']
                        .replace(
                            "Proceedings, ", "", 1),
                        "pub_info": bool(result.get('pub_info', ''))
                    }
                    result['conf_info'] = render_macro_from_template(
                        name="proceedings_only",
                        template="format/record/Conference_info_macros.tpl",
                        ctx=ctx)
        return result

    @app.template_filter()
    def format_date(datetext):
        """Display date in human readable form from available metadata."""
        from inspirehep.utils.date import create_datestruct
        from invenio_utils.date import convert_datestruct_to_dategui

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
                return datestruct[0]
