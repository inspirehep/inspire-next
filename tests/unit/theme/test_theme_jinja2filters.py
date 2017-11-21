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

from __future__ import absolute_import, division, print_function

import jinja2
import pytest
from elasticsearch_dsl import result
from flask import current_app
from mock import Mock, patch

from inspirehep.modules.records.wrappers import LiteratureRecord
from inspirehep.modules.theme.jinja2filters import (
    ads_links,
    apply_template_on_array,
    author_profile,
    author_urls,
    back_to_search_link,
    citation_phrase,
    collection_select_current,
    conference_date,
    construct_date_format,
    email_link,
    email_links,
    epoch_to_year_format,
    experiment_date,
    experiment_link,
    find_collection_from_url,
    format_author_name,
    format_cnum_with_slash,
    format_cnum_with_hyphons,
    format_date,
    institutes_links,
    is_cataloger,
    is_external_link,
    is_list,
    is_upper,
    join_array,
    join_nested_lists,
    json_dumps,
    limit_facet_elements,
    link_to_hep_affiliation,
    new_line_after,
    proceedings_link,
    publication_info,
    remove_duplicates_from_list,
    sanitize_arxiv_pdf,
    sanitize_collection_name,
    search_for_experiments,
    show_citations_number,
    sort_list_by_dict_val,
    strip_leading_number_plot_caption,
    url_links,
    words,
    words_to_end,
)

from mocks import MockUser


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
        return lambda o, s: {'titles': [{'title': title}],
                             'control_number': control_numbers_map[o['$ref']]}
    return get_replace_refs_mock


@pytest.fixture
def mock_perform_es_search():
    return result.Response(
        {
            "hits": {
                "hits": [
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "elasticsearch",
                        "_score": 12.0,

                        "_source": {
                            "title": "Higgs Discovery"
                        },
                    },
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "42",
                        "_score": 11.123,

                        "_source": {
                            "title": "Another Higgs Discovery"
                        },
                    },
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "47",
                        "_score": 1,

                        "_source": {
                            "title": "And another Higgs Discovery"
                        },
                    },
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "53",
                        "_score": 16.0,
                    },
                ],
                "max_score": 12.0,
                "total": 10
            },
            "timed_out": False,
            "took": 123
        }
    )


@pytest.fixture
def mock_perform_es_search_empty():
    return result.Response(
        {
            "hits": {
                "total": 0,
                "max_score": 'null',
                "hits": []
            }
        }
    )


@pytest.fixture
def mock_perform_es_search_onerecord():
    return result.Response(
        {
            "hits": {
                "hits": [
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "42",
                        "_score": 11.123,

                        "_source": {
                            "control_number": 1410174
                        }
                    }
                ],
                "max_score": 11.123,
                "total": 1
            },
            "timed_out": False,
            "took": 123
        }
    )


@pytest.fixture
def mock_perform_es_search_tworecord():
    return result.Response(
        {
            "hits": {
                "hits": [
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "42",
                        "_score": 11.123,

                        "_source": {
                            "control_number": 1407068,
                            'dois': [
                                {
                                    'source': 'Elsevier',
                                    'value': u'10.1016/j.ppnp.2015.10.002'
                                }
                            ]
                        }
                    },
                    {
                        "_index": "records-hep",
                        "_type": "hep",
                        "_id": "43",
                        "_score": 11.123,

                        "_source": {
                            "control_number": 1407079
                        }
                    }
                ],
                "max_score": 11.123,
                "total": 2
            }
        }
    )


@patch('inspirehep.modules.theme.jinja2filters.current_app.jinja_env.get_template')
def test_apply_template_on_array_returns_empty_list_on_empty_list(g_t, jinja_env):
    g_t.return_value = jinja_env.from_string('{{ content }}')

    expected = []
    result = apply_template_on_array([], 'banana')

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.current_app.jinja_env.get_template')
def test_apply_template_on_array_applies_template(g_t, jinja_env):
    g_t.return_value = jinja_env.from_string('{{ content }}')

    expected = ['foo']
    result = apply_template_on_array(['foo'], 'banana')

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.current_app.jinja_env.get_template')
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
    expected = ['\n<a href="mailto:foo@example.com">foo@example.com</a>']
    result = email_links(['foo@example.com'])

    assert expected == result


def test_email_link_returns_email_link_on_element(request_context):
    expected = '\n<a href="mailto:foo@example.com">foo@example.com</a>'
    result = email_link('foo@example.com')

    assert expected == result


def test_url_links_returns_url_link_on_list_of_one_element():
    record_with_urls = {'urls': [{'value': 'http://www.example.com'}]}

    expected = ['\n<a href="http://www.example.com">http://www.example.com</a>']
    result = url_links(record_with_urls)

    assert expected == result


def test_institutes_links():
    record_with_institute = {'institute': ['foo']}

    expected = ['\n<a href="search/?cc=Institutions&p=110_u%3Afoo&of=hd">foo</a>']
    result = institutes_links(record_with_institute)

    assert expected == result


def test_author_profile():
    record_with_profile = {'profile': ['foo']}

    expected = ['\n<a href="/author/search?q=foo">foo</a>']
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


def test_remove_duplicates_from_list_returns_empty_list_on_empty_list():
    expected = []
    result = remove_duplicates_from_list([])

    assert expected == result


def test_remove_duplicates__from_list_removes_duplicates_from_non_empty_list():
    expected = ['foo', 'bar']
    result = remove_duplicates_from_list(['foo', 'bar', 'foo', 'foo', 'bar'])

    assert expected == result


def test_conference_date_returns_date_when_record_has_a_date():
    with_a_date = {'date': '26-30 Mar 2012'}

    expected = '26-30 Mar 2012'
    result = conference_date(with_a_date)

    assert expected == result


def test_conference_date_returns_empty_string_when_no_opening_date():
    no_opening_date = {'closing_date': '2015-03-21'}

    expected = ''
    result = conference_date(no_opening_date)

    assert expected == result


def test_conference_date_returns_empty_string_when_no_closing_date():
    no_closing_date = {'opening_date': '2015-03-14'}

    expected = ''
    result = conference_date(no_closing_date)

    assert expected == result


def test_conference_date_formats_date_when_same_year_same_month():
    same_year_same_month = {
        'opening_date': '2015-03-14',
        'closing_date': '2015-03-21'
    }

    expected = '14-21 Mar 2015'
    result = conference_date(same_year_same_month)

    assert expected == result


def test_conference_date_formats_date_when_same_year_different_month():
    same_year_different_month = {
        'opening_date': '2012-05-28',
        'closing_date': '2012-06-01'
    }

    expected = '28 May - 01 Jun 2012'
    result = conference_date(same_year_different_month)

    assert expected == result


def test_conference_date_formats_date_when_different_year():
    different_year = {
        'opening_date': '2012-12-31',
        'closing_date': '2013-01-01'
    }

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
    with_no_dates = {}

    assert experiment_date(with_no_dates) is None


def test_experiment_date_returns_started_with_date_started():
    with_date_started = {'date_started': '1993'}

    expected = 'Started: 1993'
    result = experiment_date(with_date_started)

    assert expected == result


def test_experiment_date_returns_proposed_with_date_started():
    with_date_started = {'date_proposed': '1993'}

    expected = 'Proposed: 1993'
    result = experiment_date(with_date_started)

    assert expected == result


def test_experiment_date_returns_approved_with_date_started():
    with_date_started = {'date_approved': '1993'}

    expected = 'Approved: 1993'
    result = experiment_date(with_date_started)

    assert expected == result


def test_experiment_date_returns_still_running_with_date_completed_9999():
    with_date_completed_9999 = {'date_completed': '9999'}

    expected = 'Still Running'
    result = experiment_date(with_date_completed_9999)

    assert expected == result


def test_experiment_date_returns_completed_with_date_completed():
    with_date_completed = {'date_completed': '1993'}

    expected = 'Completed: 1993'
    result = experiment_date(with_date_completed)

    assert expected == result


def test_proceedings_link_returns_empty_string_without_cnum():
    without_cnum = {}

    expected = ''
    result = proceedings_link(without_cnum)

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.LiteratureSearch.execute')
def test_proceedings_link_returns_empty_string_with_zero_search_results(c, mock_perform_es_search_empty):
    c.return_value = mock_perform_es_search_empty

    with_cnum = {'cnum': 'banana'}

    expected = ''
    result = proceedings_link(with_cnum)

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.LiteratureSearch.execute')
def test_proceedings_link_returns_a_link_with_one_search_result(c, mock_perform_es_search_onerecord):
    c.return_value = mock_perform_es_search_onerecord

    with_cnum = {'cnum': 'banana'}

    expected = '<a href="/record/1410174">Proceedings</a>'
    result = proceedings_link(with_cnum)

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.LiteratureSearch.execute')
def test_proceedings_link_joins_with_a_comma_and_a_space(s, mock_perform_es_search_tworecord):
    s.return_value = mock_perform_es_search_tworecord

    with_cnum = {'cnum': 'banana'}

    expected = ('Proceedings: <a href="/record/1407068">#1</a> (DOI: <a '
                'href="http://dx.doi.org/10.1016/j.ppnp.2015.10.002">'
                '10.1016/j.ppnp.2015.10.002</a>, '
                '<a href="/record/1407079">#2</a>')
    result = proceedings_link(with_cnum)

    assert expected == result


def test_experiment_link_returns_empty_list_without_related_experiments():
    without_related_experiment = {}

    expected = []
    result = experiment_link(without_related_experiment)

    assert expected == result


def test_experiment_link_returns_link_for_a_list_of_one_element():
    related_experiments_a_list_of_one_element = {
        'related_experiments': [
            {'name': 'foo'}
        ]
    }

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
    without_ICN = {}

    expected = ''
    result = link_to_hep_affiliation(without_ICN)

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.InstitutionsSearch.execute')
def test_link_to_hep_affiliation_returns_empty_string_when_empty_results(s, mock_perform_es_search_empty):
    s.return_value = mock_perform_es_search_empty

    with_ICN = {'ICN': 'CERN'}

    expected = ''
    result = link_to_hep_affiliation(with_ICN)

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.InstitutionsSearch.execute')
def test_link_to_hep_affiliation_singular_when_one_result(s, mock_perform_es_search_onerecord):
    s.return_value = mock_perform_es_search_onerecord

    with_ICN = {'ICN': 'DESY'}

    expected = '1 Paper from DESY'
    result = link_to_hep_affiliation(with_ICN)

    assert expected == result


@patch('inspirehep.modules.theme.jinja2filters.InstitutionsSearch.execute')
def test_link_to_hep_affiliation_plural_when_more_results(s, mock_perform_es_search_tworecord):
    s.return_value = mock_perform_es_search_tworecord

    with_ICN = {'ICN': 'Fermilab'}

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


def test_limit_facet_elements():
    config = {'FACETS_SIZE_LIMIT': 2}

    with patch.dict(current_app.config, config):
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
    without_name = {}

    expected = ''
    result = ads_links(without_name)

    assert expected == result


def test_ads_links_builds_link_from_full_name():
    with_full_name = {
        'name': {'value': 'Ellis, John R.'}
    }

    expected = 'http://adsabs.harvard.edu/cgi-bin/author_form?author=Ellis,+J&fullauthor=Ellis,+John+R.'
    result = ads_links(with_full_name)

    assert expected == result


def test_ads_links_uses_preferred_name_when_name_has_no_lastname():
    without_last_name = {
        'name': {
            'value': ', John R.',
            'preferred_name': 'Ellis, John R.'
        }
    }

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


def test_is_upper_returns_true_when_all_uppercase():
    assert is_upper('FOO')


def test_is_upper_returns_false_when_not_all_uppercase():
    assert not is_upper('foo')


def test_format_author_name():
    expected = 'baz bar foo'
    result = format_author_name('foo,bar,baz')

    assert expected == result


def test_strip_leading_number_plot_caption():
    expected = 'foo'
    result = strip_leading_number_plot_caption('00000 foo')

    assert expected == result


def test_json_dumps():
    expected = '{"foo": ["bar", "baz"]}'
    result = json_dumps({'foo': ['bar', 'baz']})

    assert expected == result


def test_publication_info_returns_empty_dict_when_no_publication_info():
    without_publication_info = {}

    expected = {}
    result = publication_info(without_publication_info)

    assert expected == result


def test_publication_info_an_empty_list():
    an_empty_list = LiteratureRecord({'publication_info': []})

    expected = {}
    result = publication_info(an_empty_list)

    assert expected == result


def test_publication_info_a_list_of_one_element():
    a_list_of_one_element = LiteratureRecord({
        'publication_info': [
            {'journal_title': 'Int.J.Mod.Phys.'}
        ]
    })

    expected = {'pub_info': ['<i>Int.J.Mod.Phys.</i>']}
    result = publication_info(a_list_of_one_element)

    assert expected == result


def test_publication_info_a_list_of_two_elements():
    a_list_of_two_elements = LiteratureRecord({
        'publication_info': [
            {
                'journal_volume': '8',
                'journal_title': 'JINST',
                'artid': 'P09009',
                'year': 2013
            },
            {
                'journal_volume': '8',
                'journal_title': 'JINST',
                'page_start': '9009',
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
    with_journal_title_and_journal_volume = LiteratureRecord({
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
    with_journal_title_and_year = LiteratureRecord({
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
    with_journal_title_and_journal_issue = LiteratureRecord({
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
    with_journal_title_and_pages_artid = LiteratureRecord({
        'publication_info': [
            {
                'journal_title': 'Astrophys.J.',
                'page_start': '525'
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
    with_pubinfo_freetext = LiteratureRecord({
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


@patch('inspirehep.modules.records.wrappers.replace_refs')
def test_publication_info_from_conference_recid_and_parent_recid(r_r, mock_replace_refs):
    conf_rec = {'$ref': 'http://x/y/976391'}
    parent_rec = {'$ref': 'http://x/y/1402672'}
    with_title = '2005 International Linear Collider Workshop (LCWS 2005)'

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 976391),
                                                     (parent_rec, 1402672)])

    with_conference_recid_and_parent_recid = LiteratureRecord({
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


@patch('inspirehep.modules.records.wrappers.replace_refs')
def test_publication_info_from_conference_recid_and_parent_recid_with_pages(r_r, mock_replace_refs):
    with_title = '50th Rencontres de Moriond on EW Interactions and Unified Theories'
    conf_rec = {'$ref': 'http://x/y/1331207'}
    parent_rec = {'$ref': 'http://x/y/1402672'}

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 1331207),
                                                     (parent_rec, 1402672)])

    with_conference_recid_and_parent_recid_and_pages = LiteratureRecord({
        'publication_info': [
            {
                'conference_record': conf_rec,
                'parent_record': parent_rec,
                'page_start': '515',
                'page_end': '518'
            }
        ]
    })

    expected = {
        'conf_info': 'Published in <a href="/record/1402672">proceedings</a> '
                     'of <a href="/record/1331207">50th Rencontres de Moriond '
                     'on EW Interactions and Unified Theories</a>, pages\n  '
                     '515-518'
    }
    result = publication_info(with_conference_recid_and_parent_recid_and_pages)

    assert expected == result


@patch('inspirehep.modules.records.wrappers.replace_refs')
def test_publication_info_with_pub_info_and_conf_info(r_r, mock_replace_refs):
    with_title = '2005 International Linear Collider Workshop (LCWS 2005)'
    conf_rec = {'$ref': 'http://x/y/976391'}
    parent_rec = {'$ref': 'http://x/y/706120'}

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 976391),
                                                     (parent_rec, 706120)])

    with_pub_info_and_conf_info = LiteratureRecord({
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


@patch('inspirehep.modules.records.wrappers.replace_refs')
def test_publication_info_with_pub_info_and_conf_info_not_found(r_r):
    conf_rec = {'$ref': 'http://x/y/976391'}
    parent_rec = {'$ref': 'http://x/y/706120'}

    r_r.return_value = None

    with_pub_info_and_conf_info = LiteratureRecord({
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
        'pub_info': ['<i>eConf</i> C050318']
    }
    result = publication_info(with_pub_info_and_conf_info)

    assert expected == result


@patch('inspirehep.modules.records.wrappers.replace_refs')
def test_publication_info_from_conference_recid_and_not_parent_recid(r_r, mock_replace_refs):
    with_title = '20th International Workshop on Deep-Inelastic Scattering and Related Subjects'
    conf_rec = {'$ref': 'http://x/y/1086512'}

    r_r.side_effect = mock_replace_refs(with_title, [(conf_rec, 1086512)])

    with_conference_recid_without_parent_recid = LiteratureRecord({
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
    without_conference_recid_with_parent_recid = LiteratureRecord({
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


def test_format_date_handles_iso8601_dates():
    assert format_date('1993') == '1993'
    assert format_date('1993-02') == 'Feb, 1993'
    assert format_date('1993-02-02') == 'Feb 2, 1993'


def test_format_date_returns_none_when_date_is_none():
    assert format_date(None) is None


def test_find_collection_from_url_conferences():
    assert find_collection_from_url('http://localhost:5000/conferences') == 'conferences'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=conferences&q=') == 'conferences'


def test_find_collection_from_url_jobs():
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=jobs') == 'jobs'


def test_find_collection_from_url_data():
    assert find_collection_from_url('http://localhost:5000/data') == 'data'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=data&q=') == 'data'


def test_find_collection_from_url_institutions():
    assert find_collection_from_url('http://localhost:5000/institutions') == 'institutions'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=institutions&q=') == 'institutions'


def test_find_collection_from_url_journals():
    assert find_collection_from_url('http://localhost:5000/journals') == 'journals'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=journals&q=') == 'journals'


def test_find_collection_from_url_experiments():
    assert find_collection_from_url('http://localhost:5000/experiments') == 'experiments'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=experiments&q=') == 'experiments'


def test_find_collection_from_url_authors():
    assert find_collection_from_url('http://localhost:5000/authors') == 'authors'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=authors&q=') == 'authors'


def test_find_collection_from_url_literature():
    assert find_collection_from_url('http://localhost:5000') == 'literature'
    assert find_collection_from_url('http://localhost:5000/literature') == 'literature'
    assert find_collection_from_url('http://localhost:5000/search?page=1&size=25&cc=literature&q=') == 'literature'


@pytest.mark.xfail(reason='missing spaces')
def test_show_citations_number():
    assert show_citations_number(100) == 'View all 100 citations'


def test_is_external_link_when_link_is_external():
    assert is_external_link('http://www.example.com')


def test_is_external_link_when_link_is_to_a_picture():
    assert not is_external_link('http://www.example.com/foo.png')


def test_is_cataloger():
    cataloger = MockUser('cataloger@example.com', roles=['cataloger'])
    assert is_cataloger(cataloger)


def test_is_cataloger_returns_true_when_user_is_a_superuser():
    superuser = MockUser('superadmin@example.com', roles=['superuser'])
    assert is_cataloger(superuser)


def test_is_cataloger_returns_false_when_user_has_no_roles():
    user = MockUser('user@example.com')
    assert not is_cataloger(user)


@patch('inspirehep.modules.theme.jinja2filters.url_decode')
def test_back_to_search_link_handles_unicode_title(mocked_url_decode):
    collection = 'HEP'
    unicode_query = u'Göbel, Carla'
    url_map = {'q': unicode_query}

    mocked_referrer = Mock()
    mocked_url_decode.return_value = url_map

    assert back_to_search_link(mocked_referrer, collection)
