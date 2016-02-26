# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

import datetime

import jinja2
import mock
import pytest

from inspirehep.modules.theme.jinja2filters import *

from invenio_records.api import Record


@pytest.fixture
def jinja_env():
    return jinja2.Environment()


@pytest.fixture
def jinja_mock_env():
    class JinjaMockEnv(object):
        @property
        def autoescape(self):
            return True

    return JinjaMockEnv()


@pytest.fixture
def mock_replace_refs():
    def get_replace_refs_mock(title, control_numbers):
        control_numbers_map = {c[0]['$ref']: c[1] for c in control_numbers}
        return lambda o, s: {'title': title,
                             'control_number': control_numbers_map[o['$ref']]}
    return get_replace_refs_mock


@mock.patch(
    'inspirehep.modules.theme.jinja2filters.current_app.config',
    {'SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING': {'foo': 'bar'}})
def test_collection_to_index_fetches_from_mapping():
    expected = 'bar'
    result = collection_to_index('foo')

    assert expected == result


@mock.patch(
    'inspirehep.modules.theme.jinja2filters.current_app.config',
    {'SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING': {'foo': 'bar'}})
def test_collection_to_index_falls_back_to_records_hep_if_no_key():
    expected = 'records-hep'
    result = collection_to_index('baz')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.current_app.config', {})
def test_collection_to_index_falls_back_to_records_hep_if_no_mapping():
    expected = 'records-hep'
    result = collection_to_index('foo')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.current_app.jinja_env.get_template')
def test_apply_template_on_array_returns_empty_list_on_empty_list(g_t, jinja_env):
    g_t.return_value = jinja_env.from_string('{{ content }}')

    expected = []
    result = apply_template_on_array([], 'banana')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.current_app.jinja_env.get_template')
def test_apply_template_on_array_applies_template(g_t, jinja_env):
    g_t.return_value = jinja_env.from_string('{{ content }}')

    expected = ['foo']
    result = apply_template_on_array(['foo'], 'banana')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.current_app.jinja_env.get_template')
def test_apply_template_on_array_accepts_strings_as_a_list_of_one_element(g_t, jinja_env):
    g_t.return_value = jinja_env.from_string('{{ content }}')

    expected = ['foo']
    result = apply_template_on_array('foo', 'banana')

    assert expected == result


def test_apply_template_on_array_returns_empty_list_on_non_iterable():
    expected = []
    result = apply_template_on_array(0, 'banana')

    assert expected == result


def test_join_array_returns_empty_string_on_empty_list(jinja_mock_env):
    expected = ''
    result = join_array(jinja_mock_env, [], ':')

    assert expected == result


def test_join_array_adds_no_separator_on_a_list_of_one_element(jinja_mock_env):
    expected = 'foo'
    result = join_array(jinja_mock_env, ['foo'], '|')

    assert expected == result


def test_join_array_accepts_strings_as_a_list_of_one_element(jinja_mock_env):
    expected = 'foo'
    result = join_array(jinja_mock_env, 'foo', ' ')

    assert expected == result


def test_join_array_joins_with_a_separator(jinja_mock_env):
    expected = 'foo,bar'
    result = join_array(jinja_mock_env, ['foo', 'bar'], ',')

    assert expected == result


def test_new_line_after_adds_a_break():
    expected = 'foo<br>'
    result = new_line_after('foo')

    assert expected == result


def test_new_line_after_adds_no_break_after_empty_string():
    expected = ''
    result = new_line_after('')

    assert expected == result


def test_email_links_returns_email_link_on_list_of_one_element():
    expected = ['\n\n<a href="mailto:foo@example.com">foo@example.com</a>']
    result = email_links(['foo@example.com'])

    assert expected == result


def test_url_links_returns_url_link_on_list_of_one_element():
    record_with_urls = Record({'urls': [{'value': 'http://www.example.com'}]})

    expected = ['\n\n<a href="http://www.example.com">http://www.example.com</a>']
    result = url_links(record_with_urls)

    assert expected == result


def test_institutes_links():
    record_with_institute = Record({'institute': ['foo']})

    expected = ['\n\n<a href="search/?cc=Institutions&p=110_u%3Afoo&of=hd">foo</a>']
    result = institutes_links(record_with_institute)

    assert expected == result


def test_author_profile():
    record_with_profile = Record({'profile': ['foo']})

    expected = ['\n\n<a href="/author/search?q=foo">foo</a>']
    result = author_profile(record_with_profile)

    assert expected == result


def test_words():
    expected = 'foo bar'
    result = words('foo bar baz', 2)

    assert expected == result


def test_end_words():
    expected = 'bar baz'
    result = words_to_end('foo bar baz', 1)

    assert expected == result


def test_is_list_returns_true_for_a_list():
    assert is_list([])


def test_is_list_returns_none_for_something_not_a_list():
    assert is_list('foo') is None


def test_remove_duplicates_returns_empty_list_on_empty_list():
    expected = []
    result = remove_duplicates([])

    assert expected == result


def test_remove_duplicates_removes_duplicates_from_list_with_elements():
    expected = ['foo', 'bar']
    result = remove_duplicates(['foo', 'bar', 'foo', 'foo', 'bar'])

    assert expected == result


def test_has_space_returns_true_if_space():
    assert has_space('foo bar')


def test_has_space_returns_none_if_no_space():
    assert has_space('foo') is None


def test_count_words():
    expected = 3
    result = count_words('foo, bar baz')

    assert expected == result


def test_remove_duplicates_from_dict_removes_duplicates():
    list_of_dicts_with_duplicates = [
        {'a': 123, 'b': 1234},
        {'a': 3222, 'b': 1234},
        {'a': 123, 'b': 1234}
    ]

    expected = [{'a': 123, 'b': 1234}, {'a': 3222, 'b': 1234}]
    result = remove_duplicates_from_dict(list_of_dicts_with_duplicates)

    assert expected == result


def test_conference_date_returns_date_when_record_has_a_date():
    with_a_date = Record({'date': '26-30 Mar 2012'})

    expected = '26-30 Mar 2012'
    result = conference_date(with_a_date)

    assert expected == result


def test_conference_date_returns_empty_string_when_no_opening_date():
    no_opening_date = Record({'closing_date': '2015-03-21'})

    expected = ''
    result = conference_date(no_opening_date)

    assert expected == result


def test_conference_date_returns_empty_string_when_no_closing_date():
    no_closing_date = Record({'opening_date': '2015-03-14'})

    expected = ''
    result = conference_date(no_closing_date)

    assert expected == result


def test_conference_date_formats_date_when_same_year_same_month():
    same_year_same_month = Record({
        'opening_date': '2015-03-14',
        'closing_date': '2015-03-21'
    })

    expected = '14-21 Mar 2015'
    result = conference_date(same_year_same_month)

    assert expected == result


def test_conference_date_formats_date_when_same_year_different_month():
    same_year_different_month = Record({
        'opening_date': '2012-05-28',
        'closing_date': '2012-06-01'
    })

    expected = '28 May - 01 Jun 2012'
    result = conference_date(same_year_different_month)

    assert expected == result


def test_conference_date_formats_date_when_different_year():
    different_year = Record({
        'opening_date': '2012-12-31',
        'closing_date': '2013-01-01'
    })

    expected = '31 Dec 2012 - 01 Jan 2013'
    result = conference_date(different_year)

    assert expected == result


def test_search_for_experiments_returns_empty_string_on_empty_list():
    expected = ''
    result = search_for_experiments([])

    assert expected == result


def test_search_for_experiments_returns_a_link_on_a_list_of_one_element():
    expected = '<a href="/search?p=experiment_name:foo&cc=Experiments">foo</a>'
    result = search_for_experiments(['foo'])

    assert expected == result


def test_search_for_experiments_joins_with_a_comma_and_a_space():
    expected = (
        '<a href="/search?p=experiment_name:foo&cc=Experiments">foo</a>, '
        '<a href="/search?p=experiment_name:bar&cc=Experiments">bar</a>'
    )
    result = search_for_experiments(['foo', 'bar'])

    assert expected == result


def test_experiment_date_returns_none_with_no_dates():
    with_no_dates = Record({})

    assert experiment_date(with_no_dates) is None


def test_experiment_date_returns_started_with_date_started():
    with_date_started = Record({'date_started': '1993'})

    expected = 'Started: 1993'
    result = experiment_date(with_date_started)

    assert expected == result


def test_experiment_date_returns_still_running_with_date_completed_9999():
    with_date_completed_9999 = Record({'date_completed': '9999'})

    expected = 'Still Running'
    result = experiment_date(with_date_completed_9999)

    assert expected == result


def test_experiment_date_returns_completed_with_date_completed():
    with_date_completed = Record({'date_completed': '1993'})

    expected = 'Completed: 1993'
    result = experiment_date(with_date_completed)

    assert expected == result


def test_proceedings_link_returns_empty_string_without_cnum():
    without_cnum = Record({})

    expected = ''
    result = proceedings_link(without_cnum)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.search')
def test_proceedings_link_returns_empty_string_with_zero_search_results(s):
    s.return_value = {'hits': {'hits': []}}

    with_cnum = Record({'cnum': 'banana'})

    expected = ''
    result = proceedings_link(with_cnum)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.search')
def test_proceedings_link_returns_a_link_with_one_search_result(s):
    s.return_value = {
        'hits': {
            'hits': [
                Record({'control_number': '1410174'})
            ]
        }
    }

    with_cnum = Record({'cnum': 'banana'})

    expected = '<a href="/record/1410174">Proceedings</a>'
    result = proceedings_link(with_cnum)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.search')
def test_proceedings_link_joins_with_a_comma_and_a_space(s):
    s.return_value = {
        'hits': {
            'hits': [
                Record({
                    'control_number': '1407068',
                    'dois': [
                        {
                            'source': 'Elsevier',
                            'value': u'10.1016/j.ppnp.2015.10.002'
                        }
                    ]
                }),
                Record({
                    'control_number': '1407079'
                })
            ]
        }
    }

    with_cnum = Record({'cnum': 'banana'})

    expected = ('Proceedings: <a href="/record/1407068">#1</a> (DOI: <a '
                'href="http://dx.doi.org/10.1016/j.ppnp.2015.10.002">'
                '10.1016/j.ppnp.2015.10.002</a>, '
                '<a href="/record/1407079">#2</a>')
    result = proceedings_link(with_cnum)

    assert expected == result


def test_experiment_link_returns_empty_list_without_related_experiments():
    without_related_experiment = Record({})

    expected = []
    result = experiment_link(without_related_experiment)

    assert expected == result


def test_experiment_link_returns_link_for_a_list_of_one_element():
    related_experiments_a_list_of_one_element = Record({
        'related_experiments': [
            {'name': 'foo'}
        ]
    })

    expected = ['<a href=/search?cc=Experiments&p=experiment_name:foo>foo</a>']
    result = experiment_link(related_experiments_a_list_of_one_element)

    assert expected == result


def test_format_cnum_with_slash_replaces_dash_with_slash():
    expected = 'C12/03/26.1'
    result = format_cnum_with_slash('C12-03-26.1')

    assert expected == result


def test_format_cnum_with_hyphons():
    expected = 'C12-03-26.1'
    result = format_cnum_with_hyphons('C12-03-26.1')

    assert expected == result


def test_link_to_hep_affiliation_returns_empty_string_when_record_has_no_ICN():
    without_ICN = Record({})

    expected = ''
    result = link_to_hep_affiliation(without_ICN)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.search')
def test_link_to_hep_affiliation_returns_empty_string_when_empty_results(s):
    s.return_value = {'hits': {'hits': []}}

    with_ICN = Record({'ICN': 'CERN'})

    expected = ''
    result = link_to_hep_affiliation(with_ICN)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.search')
def test_link_to_hep_affiliation_singular_when_one_result(s):
    s.return_value = {'hits': {'hits': [{}]}}

    with_ICN = Record({'ICN': 'DESY'})

    expected = '1 Paper from DESY'
    result = link_to_hep_affiliation(with_ICN)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.search')
def test_link_to_hep_affiliation_plural_when_more_results(s):
    s.return_value = {'hits': {'hits': [{}, {}]}}

    with_ICN = Record({'ICN': 'Fermilab'})

    expected = '2 Papers from Fermilab'
    result = link_to_hep_affiliation(with_ICN)

    assert expected == result


def test_join_nested_lists():
    expected = 'foo bar baz'
    result = join_nested_lists([['foo', 'bar'], ['baz']], ' ')

    assert expected == result


def test_sanitize_collection_name_returns_none_on_empty_string():
    assert sanitize_collection_name('') is None


def test_sanitize_collection_name_replaces_hepnames_with_authors():
    expected = 'authors'
    result = sanitize_collection_name('hepnames')

    assert expected == result


def test_sanitize_collection_name_replaces_hep_with_literature():
    expected = 'literature'
    result = sanitize_collection_name('hep')

    assert expected == result


def test_collection_select_current_returns_active_if_equal():
    expected = 'active'
    result = collection_select_current('foo', 'FOO')

    assert expected == result


def test_collection_select_current_returns_empty_string_if_different():
    expected = ''
    result = collection_select_current('foo', 'bar')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.es.count')
def test_number_of_records(c):
    c.return_value = {'count': 1337}

    expected = 1337
    result = number_of_records('foo')

    assert expected == result


def test_sanitize_arxiv_pdf_removes_arxiv_prefix():
    expected = '0808.1819.pdf'
    result = sanitize_arxiv_pdf('arXiv:0808.1819')

    assert expected == result


def test_sort_list_by_dict_val():
    expected = [
        {'doc_count': 2},
        {'doc_count': 1},
        {'doc_count': 0}
    ]
    result = sort_list_by_dict_val([
        {'doc_count': 1},
        {'doc_count': 0},
        {'doc_count': 2}
    ])

    assert expected == result


def test_epoch_to_year_format():
    expected = '1993'
    result = epoch_to_year_format('728632800000')

    assert expected == result


def test_construct_date_format():
    expected = '1993-02-02->1993-12-31'
    result = construct_date_format('728632800000')

    assert expected == result


@mock.patch(
    'inspirehep.modules.theme.jinja2filters.current_app.config',
    {'FACETS_SIZE_LIMIT': 2})
def test_limit_facet_elements():
    expected = ['foo', 'bar']
    result = limit_facet_elements(['foo', 'bar', 'baz'])

    assert expected == result


def test_author_urls_returns_empty_string_on_empty_list():
    expected = ''
    result = author_urls([], ',')

    assert expected == result


def test_author_urls_builds_url_on_list_of_one_element():
    expected = '<a href="/search?ln=en&amp;cc=HepNames&amp;p=name:foo&amp;of=hd">foo</a>'
    result = author_urls([{'name': 'foo'}], '|')

    assert expected == result


def test_author_urls_joins_with_the_separator():
    expected = '<a href="/search?ln=en&amp;cc=HepNames&amp;p=name:foo&amp;of=hd">foo</a>, <a href="/search?ln=en&amp;cc=HepNames&amp;p=name:bar&amp;of=hd">bar</a>'
    result = author_urls([{'name': 'foo'}, {'name': 'bar'}], ', ')

    assert expected == result


def test_ads_links_returns_empty_string_when_record_has_no_name():
    without_name = Record({})

    expected = ''
    result = ads_links(without_name)

    assert expected == result


def test_ads_links_builds_link_from_full_name():
    with_full_name = Record({
        'name': {'value': 'Ellis, John R.'}
    })

    expected = 'http://adsabs.harvard.edu/cgi-bin/author_form?author=Ellis,+J&fullauthor=Ellis,+John+R.'
    result = ads_links(with_full_name)

    assert expected == result


def test_ads_links_uses_preferred_name_when_name_has_no_lastname():
    without_last_name = Record({
        'name': {
            'value': ', John R.',
            'preferred_name': 'Ellis, John R.'
        }
    })

    expected = 'http://adsabs.harvard.edu/cgi-bin/author_form?author=Ellis, John R.'
    result = ads_links(without_last_name)

    assert expected == result


def test_citation_phrase_singular_with_one_citation():
    expected = 'Cited 1 time'
    result = citation_phrase(1)

    assert expected == result


def test_citation_phrase_plural_with_zero_citations():
    expected = 'Cited 0 times'
    result = citation_phrase(0)

    assert expected == result


def test_citation_phrase_plural_with_more_citations():
    expected = 'Cited 2 times'
    result = citation_phrase(2)

    assert expected == result


@mock.patch(
    'inspirehep.modules.theme.jinja2filters.session',
    {
        'last-queryfoobar': {
            'number_of_hits': 1337,
            'timestamp': datetime.datetime(
                1993, 2, 2, 5, 57, 0, 0)}})
@mock.patch('inspirehep.modules.theme.jinja2filters.datetime')
def test_number_of_search_results_fetches_from_session(mock_datetime):
    mock_datetime.datetime.utcnow.return_value = datetime.datetime(1993, 2, 2, 6, 0, 0, 0)

    expected = 1337
    result = number_of_search_results('foo', 'bar')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.session', {})
@mock.patch('inspirehep.modules.theme.jinja2filters.es.count')
def test_number_of_search_results_falls_back_to_query(c):
    c.return_value = {'count': 1337}

    expected = 1337
    result = number_of_search_results('foo', 'bar')

    assert expected == result


def test_is_upper_returns_true_when_all_uppercase():
    assert is_upper('FOO')


def test_is_upper_returns_false_when_not_all_uppercase():
    assert not is_upper('foo')


def test_split_author_name():
    expected = 'baz bar foo'
    result = split_author_name('foo,bar,baz')

    assert expected == result


def test_strip_leading_number_plot_caption():
    expected = 'foo'
    result = strip_leading_number_plot_caption('00000 foo')

    assert expected == result


def test_publication_info_returns_empty_dict_when_no_publication_info():
    without_publication_info = Record({})

    expected = {}
    result = publication_info(without_publication_info)

    assert expected == result


def test_publication_info_an_empty_list():
    an_empty_list = Record({'publication_info': []})

    expected = {}
    result = publication_info(an_empty_list)

    assert expected == result


def test_publication_info_a_list_of_one_element():
    a_list_of_one_element = Record({
        'publication_info': [
            {'journal_title': 'Int.J.Mod.Phys.'}
        ]
    })

    expected = {'pub_info': ['<i>Int.J.Mod.Phys.</i>']}
    result = publication_info(a_list_of_one_element)

    assert expected == result


def test_publication_info_a_list_of_two_elements():
    a_list_of_two_elements = Record({
        'publication_info': [
            {
                'journal_volume': '8',
                'journal_title': 'JINST',
                'page_artid': 'P09009',
                'year': 2013
            },
            {
                'journal_volume': '8',
                'journal_title': 'JINST',
                'page_artid': '9009',
                'year': 2013
            }
        ]
    })

    expected = {
        'pub_info': [
            '<i>JINST</i> 8 (2013) P09009',
            '<i>JINST</i> 8 (2013) 9009'
        ]
    }
    result = publication_info(a_list_of_two_elements)

    assert expected == result


def test_publication_info_from_journal_title_and_journal_volume():
    with_journal_title_and_journal_volume = Record({
        'publication_info': [
            {
                'journal_title': 'JHEP',
                'journal_volume': '1508'
            }
        ]
    })

    expected = {
        'pub_info': [
            '<i>JHEP</i> 1508'
        ]
    }
    result = publication_info(with_journal_title_and_journal_volume)

    assert expected == result


def test_publication_info_from_journal_title_and_year():
    with_journal_title_and_year = Record({
        'publication_info': [
            {
                'journal_title': 'Eur.Phys.J.',
                'year': 2015
            }
        ]
    })

    expected = {
        'pub_info': [
            '<i>Eur.Phys.J.</i> (2015)'
        ]
    }
    result = publication_info(with_journal_title_and_year)

    assert expected == result


def test_publication_info_from_journal_title_and_journal_issue():
    with_journal_title_and_journal_issue = Record({
        'publication_info': [
            {
                'journal_title': 'JINST',
                'journal_issue': '02'
            }
        ]
    })

    expected = {
        'pub_info': [
            '<i>JINST</i> 02, '
        ]
    }
    result = publication_info(with_journal_title_and_journal_issue)

    assert expected == result


def test_publication_info_from_journal_title_and_pages_artid():
    with_journal_title_and_pages_artid = Record({
        'publication_info': [
            {
                'journal_title': 'Astrophys.J.',
                'page_artid': '525'
            }
        ]
    })

    expected = {
        'pub_info': [
            '<i>Astrophys.J.</i> 525'
        ]
    }
    result = publication_info(with_journal_title_and_pages_artid)

    assert expected == result


def test_publication_info_from_pubinfo_freetext():
    with_pubinfo_freetext = Record({
        'publication_info': [
            {'pubinfo_freetext': 'Phys. Rev. 127 (1962) 965-970'}
        ]
    })

    expected = {
        'pub_info': [
            'Phys. Rev. 127 (1962) 965-970'
        ]
    }
    result = publication_info(with_pubinfo_freetext)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.replace_refs')
def test_publication_info_from_conference_recid_and_parent_recid(r_r, mock_replace_refs):
    conf_rec = {'$ref': 'http://x/y/976391'}
    parent_rec = {'$ref': 'http://x/y/1402672'}
    with_title = '2005 International Linear Collider Workshop (LCWS 2005)'

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 976391),
                                                     (parent_rec, 1402672)])

    with_conference_recid_and_parent_recid = Record({
        'publication_info': [
            {
                'conference_record': conf_rec,
                'parent_record': parent_rec
            }
        ]
    })

    expected = {
        'conf_info': 'Published in <a href="/record/1402672">proceedings</a> '
                     'of <a href="/record/976391">2005 International Linear '
                     'Collider Workshop (LCWS 2005)</a>'
    }
    result = publication_info(with_conference_recid_and_parent_recid)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.replace_refs')
def test_publication_info_from_conference_recid_and_parent_recid_with_pages(r_r, mock_replace_refs):
    with_title = '50th Rencontres de Moriond on EW Interactions and Unified Theories'
    conf_rec = {'$ref': 'http://x/y/1331207'}
    parent_rec = {'$ref': 'http://x/y/1402672'}

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 1331207),
                                                     (parent_rec, 1402672)])

    with_conference_recid_and_parent_recid_and_pages = Record({
        'publication_info': [
            {
                'conference_record': conf_rec,
                'parent_record': parent_rec,
                'page_artid': '515-518'
            }
        ]
    })

    expected = {
        'conf_info': 'Published in <a href="/record/1402672">proceedings</a> '
                     'of <a href="/record/1331207">50th Rencontres de Moriond '
                     'on EW Interactions and Unified Theories</a>, pages  \n  '
                     '515-518'
    }
    result = publication_info(with_conference_recid_and_parent_recid_and_pages)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.replace_refs')
def test_publication_info_with_pub_info_and_conf_info(r_r, mock_replace_refs):
    with_title = '2005 International Linear Collider Workshop (LCWS 2005)'
    conf_rec = {'$ref': 'http://x/y/976391'}
    parent_rec = {'$ref': 'http://x/y/706120'}

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 976391),
                                                     (parent_rec, 706120)])

    with_pub_info_and_conf_info = Record({
        'publication_info': [
            {
                'journal_title': 'eConf',
                'journal_volume': 'C050318'
            },
            {
                'conference_record': conf_rec,
                'parent_record': parent_rec
            }
        ]
    })

    expected = {
        'conf_info': '(<a href="/record/706120">Proceedings</a> of <a '
                     'href="/record/976391">\n  2005 International Linear '
                     'Collider Workshop (LCWS 2005)</a>)',
        'pub_info': ['<i>eConf</i> C050318']
    }
    result = publication_info(with_pub_info_and_conf_info)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.replace_refs')
def test_publication_info_from_conference_recid_and_not_parent_recid(r_r, mock_replace_refs):
    with_title = '20th International Workshop on Deep-Inelastic Scattering and Related Subjects'
    conf_rec = {'$ref': 'http://x/y/1086512'}

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 1086512)])

    with_conference_recid_without_parent_recid = Record({
        'publication_info': [
            {'conference_record': conf_rec}
        ]
    })

    expected = {
        'conf_info': 'Contribution to <a href="/record/1086512">20th '
                     'International Workshop on Deep-Inelastic Scattering '
                     'and Related Subjects</a>'
    }
    result = publication_info(with_conference_recid_without_parent_recid)

    assert expected == result


@pytest.mark.xfail(reason='pid searched in the wrong collection')
def test_publication_info_from_not_conference_recid_and_parent_recid():
    without_conference_recid_with_parent_recid = Record({
        'publication_info': [
            {'parent_record': {'$ref': 'http://x/y/720114'}}
        ]
    })

    expected = {
        'conf_info': 'Published in <a href="/record/720114">proceedings</a> '
                     'of 2005 International Linear Collider Physics and '
                     'Detector Workshop and 2nd ILC Accelerator Workshop '
                     '(Snowmass 2005)'
    }
    result = publication_info(without_conference_recid_with_parent_recid)

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.create_datestruct')
def test_format_date_returns_none_when_datestruct_is_none(c_d):
    c_d.return_value = None

    assert format_date('banana') is None


@mock.patch('inspirehep.modules.theme.jinja2filters.create_datestruct')
def test_format_date_returns_none_when_datestruct_has_one_element(c_d):
    c_d.return_value = (1993,)

    expected = 1993
    result = format_date('banana')

    assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.create_datestruct')
def test_format_date_returns_none_when_no_datestruct(c_d, app):
    with app.test_request_context():
        c_d.return_value = (1993, 2)

        expected = 'Feb, 1993'
        result = format_date('banana')

        assert expected == result


@mock.patch('inspirehep.modules.theme.jinja2filters.create_datestruct')
def test_format_date_returns_none_when_no_datestruct(c_d, app):
    with app.test_request_context():
        c_d.return_value = (1993, 2, 2)

        expected = 'Feb 2, 1993'
        result = format_date('banana')

        assert expected == result


def test_is_external_link():
    assert is_external_link('http')


def test_is_institute():
    assert is_institute('kekscan')


def test_weblinks():
    """In case a description is given and found in the dictionary"""
    assert weblinks('CLNS97') == 'Cornell Document Server'

    """In case description is given but NOT found in the dictionary"""
    assert weblinks('none') == 'Link to none'

    """In case no description is given"""
    assert weblinks('') == 'Link to fulltext'
