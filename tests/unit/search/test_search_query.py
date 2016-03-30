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

import pytest

from inspirehep.modules.search.query import InspireQuery


def test_empty():
    query = InspireQuery('')

    expected = {
        'query': {
            'multi_match': {
                'zero_terms_query': 'all',
                'query': '',
                'fields': [
                    'title^3',
                    'title.raw^10',
                    'abstract^2',
                    'abstract.raw^4',
                    'author^10',
                    'author.raw^15',
                    'reportnumber^10',
                    'eprint^10',
                    'doi^10'
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_google_style():
    query = InspireQuery('kudenko')

    expected = {
        'query': {
            'multi_match': {
                'zero_terms_query': 'all',
                'query': 'kudenko',
                'fields': [
                    'title^3',
                    'title.raw^10',
                    'abstract^2',
                    'abstract.raw^4',
                    'author^10',
                    'author.raw^15',
                    'reportnumber^10',
                    'eprint^10',
                    'doi^10'
                ]
            }
        }
    }
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_google_style_or_google_style():
    query = InspireQuery('sungtae cho or 1301.7261')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_google_style_and_not_collaboration():
    query = InspireQuery("raffaele d'agnolo and not cn cms")

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author():
    query = InspireQuery('a kondrashuk')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_author_bai():
    query = InspireQuery('a r.j.hill.1')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_or_author():
    query = InspireQuery('a fileviez perez,p or p. f. perez')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_and_not_author():
    query = InspireQuery('a espinosa,jose r and not a rodriguez espinosa')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_and_not_type_code():
    query = InspireQuery('a nilles,h and not tc I')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def author_or_author_and_not_collaborations_and_not_title_and_not_type_code():
    query = InspireQuery(
        'a rojo,j. or rojo-chacon,j. and not collaboration pierre auger '
        'and not collaboration auger and not t auger and tc p')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor():
    query = InspireQuery('ea wu, xing gang')

    expected = {}
    result = query.body

    assert expected == result


def test_author_colon():
    query = InspireQuery('author: vagenas')

    expected = {
        'query': {
            'bool': {
                'should': [
                    {'match': {'authors.name_variations': 'vagenas'}},
                    {'match': {'authors.full_name': 'vagenas'}}
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_author_colon_with_double_quotes():
    query = InspireQuery('author:"tachikawa, yuji"')

    expected = {
        'query': {
            'bool': {
                'must': [
                    {'match': {'authors.name_variations': 'tachikawa, yuji'}}
                ],
                'should': [
                    {'match': {'authors.full_name': 'tachikawa, yuji'}}
                ]
            }
        }
    }
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_author_colon_bai():
    query = InspireQuery('author:Y.Nomura.1')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_author_colon_bai_and_collection_colon():
    query = InspireQuery(
        'author:E.Witten.1 AND collection:citeable')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_author_colon_bai_with_double_quotes_and_collection_colon():
    query = InspireQuery('author:"E.Witten.1" AND collection:citeable')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_author_colon_bai_and_collection_colon_and_cited_colon():
    query = InspireQuery(
        'author:E.Witten.1 AND collection:citeable AND cited:500->1000000')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_author_colon_bai_with_double_quotes_and_collection_colon_and_cited_colon():
    query = InspireQuery(
        'author:"E.Witten.1" AND collection:citeable AND cited:500->1000000')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_colon_or_eprint_without_keyword():
    query = InspireQuery('author:"Takayanagi, Tadashi" or hep-th/0010101')

    expected = {}
    result = query.body

    assert expected == result


def test_author_colon_or_author_colon_or_title_colon_or_title_colon():
    query = InspireQuery(
        "(author:'Hiroshi Okada' OR (author:'H Okada' hep-ph) OR "
        "title: 'Dark matter in supersymmetric U(1(B-L) model' OR "
        "title: 'Non-Abelian discrete symmetry for flavors')")

    expected = {
        'query': {
            'bool': {
                'should': [
                    {
                        'bool': {
                            'should': [
                                {
                                    'bool': {
                                        'should': [
                                            {
                                                'multi_match': {
                                                    'query': 'Hiroshi Okada',
                                                    'type': 'phrase',
                                                    'fields': [
                                                        'authors.full_name',
                                                        'authors.alternative_name'
                                                    ],
                                                }
                                            },
                                            {
                                                'bool': {
                                                    'must': [
                                                        {
                                                            'multi_match': {
                                                                'query': 'H Okada',
                                                                'type': 'phrase',
                                                                'fields': [
                                                                    'authors.full_name',
                                                                    'authors.alternative_name'
                                                                ]
                                                            }
                                                        },
                                                        {
                                                            'multi_match': {
                                                                'query': 'hep-ph',
                                                                'fields': [
                                                                    'global_fulltext'
                                                                ]
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    'multi_match': {
                                        'query': 'Dark matter in supersymmetric U(1(B-L) model',
                                        'type': 'phrase',
                                        'fields': [
                                            'titles.title',
                                            'titles.title.raw^2',
                                            'title_translation.title',
                                            'title_variation',
                                            'title_translation.subtitle',
                                            'titles.subtitle'
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        'multi_match': {
                            'query': 'Non-Abelian discrete symmetry for flavors',
                            'type': 'phrase',
                            'fields': [
                                'titles.title',
                                'titles.title.raw^2',
                                'title_translation.title',
                                'title_variation',
                                'title_translation.subtitle',
                                'titles.subtitle'
                            ],
                        }
                    }
                ]
            }
        }
    }
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_citedby_colon():
    query = InspireQuery('citedby:foobar')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_citedby_colon_recid_colon():
    query = InspireQuery('citedby:recid:902780')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_eprint_colon_with_arxiv():
    query = InspireQuery('eprint:arxiv:TODO')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_eprint_colon_without_arxiv():
    query = InspireQuery('eprint:TODO')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor_colon():
    query = InspireQuery('ea:matt visser')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor_colon_and_collection_colon():
    query = InspireQuery('ea: matt visser AND collection:citeable')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_exactauthor_colon_bai():
    query = InspireQuery('exactauthor:J.Serra.3')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_or_of_exactauthor_colon_queries():
    query = InspireQuery('exactauthor:X.Yin.1 or exactauthor:"Yin, Xi"')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_fulltext_colon():
    query = InspireQuery('fulltext:TODO')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_journal_colon():
    query = InspireQuery('journal:TODO')

    expected = {}
    result = query.body

    assert expected == result


def test_refersto_colon_recid_colon():
    query = InspireQuery('refersto:recid:1286113')

    expected = {
        'query': {
            'multi_match': {
                'query': '1286113',
                'fields': [
                    'references.recid'
                ]
            }
        }
    }
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_topcite_colon():
    query = InspireQuery('topcite:200+')

    expected = {}
    result = query.body

    assert expected == result


def test_find_journal():
    query = InspireQuery('find j "Phys.Rev.Lett.,105*"')

    expected = {
        'query': {
            'multi_match': {
                'query': '"Phys.Rev.Lett.,105*"',
                'fields': [
                    'publication_info.recid',
                    'publication_info.page_artid',
                    'publication_info.journal_issue',
                    'publication_info.conf_acronym',
                    'publication_info.journal_title',
                    'publication_info.reportnumber',
                    'publication_info.confpaper_info',
                    'publication_info.journal_volume',
                    'publication_info.cnum',
                    'publication_info.pubinfo_freetext',
                    'publication_info.year_raw',
                    'publication_info.isbn',
                    'publication_info.note'
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_find_exactauthor():
    query = InspireQuery('find ea witten, edward')

    expected = {
        'query': {
            'multi_match': {
                'query': 'witten, edward',
                'fields': [
                    'exactauthor.raw',
                    'authors.full_name',
                    'authors.alternative_name'
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_find_exactauthor_not_affiliation_uppercase():
    query = InspireQuery(
        'FIND EA RINALDI, MASSIMILIANO NOT AFF SINCROTRONE TRIESTE')

    expected = {
        'query': {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': 'RINALDI, MASSIMILIANO',
                            'fields': [
                                'exactauthor.raw',
                                'authors.full_name',
                                'authors.alternative_name'
                            ]
                        }
                    },
                    {
                        'bool': {
                            'must_not': [
                                {
                                    'multi_match': {
                                        'query': 'SINCROTRONE TRIESTE',
                                        'fields': [
                                            'authors.affiliations.value',
                                            'corporate_author'
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_find_author():
    query = InspireQuery('find a polchinski')

    expected = {
        'query': {
            'bool': {
                'must': [
                    {'match': {'authors.name_variations': 'polchinski'}}
                ],
                'should': [
                    {'match': {'authors.full_name': 'polchinski'}}
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_find_author_uppercase():
    query = InspireQuery('FIND A W F CHANG')

    expected = {
        'query': {
            'bool': {
                'must': [
                    {'match': {'authors.name_variations': 'W F CHANG'}}
                ],
                'should': [
                    {'match': {'authors.full_name': 'W F CHANG'}}
                ]
            }
        }
    }
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_find_author_bai():
    query = InspireQuery('find a B.R.Safdi.1')

    expected = {}
    result = query.body

    assert expected == result


def test_find_author_and_date():
    query = InspireQuery('find a hatta and date after 2000')

    expected = {
        'query': {
            'bool': {
                'must': [
                    {
                        'bool': {
                            'must': [
                                {'match': {'authors.name_variations': 'hatta'}}
                            ],
                            'should': [
                                {'match': {'authors.full_name': 'hatta'}}
                            ]
                        }
                    },
                    {
                        'bool': {
                            'should': [
                                {'range': {'imprints.date': {'gt': '2000'}}},
                                {'range': {'preprint_date': {'gt': '2000'}}},
                                {'range': {'thesis.date': {'gt': '2000'}}},
                                {'range': {'publication_info.year': {'gt': '2000'}}}                            ]
                        }
                    }
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_find_author_or_author():
    query = InspireQuery('find a gersdorff, g or a von gersdorff, g')

    expected = {
        'query': {
            'bool': {
                'should': [
                    {
                        'bool': {
                            'must': [
                                {'match': {'authors.name_variations': 'gersdorff, g'}}
                            ],
                            'should': [
                                {'match': {'authors.full_name': 'gersdorff, g'}}
                            ]
                        }
                    },
                    {
                        'bool': {
                            'must': [
                                {'match': {'authors.name_variations': 'von gersdorff, g'}}
                            ],
                            'should': [
                                {'match': {'authors.full_name': 'von gersdorff, g'}}                            ]
                        }
                    }
                ]
            }
        }
    }
    result = query.body

    assert expected == result


def test_find_author_not_author_not_author():
    query = InspireQuery('f a ostapchenko not olinto not haungs')

    expected = {
        'query': {
            'bool': {
                'must': [
                    {
                        'bool': {
                            'must': [
                                {
                                    'bool': {
                                        'must': [{'match': {'authors.name_variations': 'ostapchenko'}}],
                                        'should': [{'match': {'authors.full_name': 'ostapchenko'}}]
                                    }
                                },
                                {
                                    'bool': {
                                        'must_not': [
                                            {
                                                'bool': {
                                                    'must': [{'match': {'authors.name_variations': 'olinto'}}],
                                                    'should': [{'match': {'authors.full_name': 'olinto'}}]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        'bool': {
                            'must_not': [
                                {
                                    'bool': {
                                        'must': [{'match': {'authors.name_variations': 'haungs'}}],
                                        'should': [{'match': {'authors.full_name': 'haungs'}}]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_caption():
    query = InspireQuery('Diagram for the fermion flow violating process')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_country_code():
    query = InspireQuery('find cc italy')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='today must be converted to an actual date')
def test_find_date():
    query = InspireQuery('fin date > today')

    expected =  {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_field_code():
    query = InspireQuery('find fc a')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_report():
    query = InspireQuery('find r atlas-conf-*')

    expected = {}
    result = query.body

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_type_code():
    query = InspireQuery('find tc book')

    expected = {}
    result = query.body

    assert expected == result
