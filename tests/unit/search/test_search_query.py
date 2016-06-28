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

from inspirehep.modules.search import IQ


def test_empty():
    query = IQ('')

    expected = {
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
    result = query.to_dict()

    assert expected == result


def test_google_style():
    query = IQ('kudenko')

    expected = {
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
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_google_style_or_google_style():
    query = IQ('sungtae cho or 1301.7261')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_google_style_and_not_collaboration():
    query = IQ("raffaele d'agnolo and not cn cms")

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author():
    query = IQ('a kondrashuk')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_bai_malformed():
    query = IQ('a r.j.hill.1')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_author_bai():
    query = IQ('find a r.j.hill.1')

    expected = {
        "bool": {
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "r.j.hill.1"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "r.j.hill.1"
                      }
                    }
                  ]
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.full_name": "r.j.hill.1"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_or_author():
    query = IQ('a fileviez perez,p or p. f. perez')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_and_not_author():
    query = IQ('a espinosa,jose r and not a rodriguez espinosa')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_and_not_type_code():
    query = IQ('a nilles,h and not tc I')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def author_or_author_and_not_collaborations_and_not_title_and_not_type_code():
    query = IQ(
        'a rojo,j. or rojo-chacon,j. and not collaboration pierre auger '
        'and not collaboration auger and not t auger and tc p')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor():
    query = IQ('ea wu, xing gang')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_abstract_colon_with_star_wildcard():
    query = IQ('abstract: part*')

    expected = {
        'query_string': {
            'query': 'part*',
            'default_field': 'abstracts.value',
            'analyze_wildcard': True
        }
    }
    result = query.to_dict()

    assert expected == result


def test_author_colon():
    query = IQ('author: vagenas')

    expected = {
        "bool": {
            "should": [
              {
                "match": {
                  "authors.name_variations": "vagenas"
                }
              },
              {
                "match": {
                  "authors.full_name": "vagenas"
                }
              },
              {
                "match": {
                  "authors.inspire_bai": "vagenas"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_author_colon_with_double_quotes():
    query = IQ('author:"tachikawa, yuji"')

    expected = {
        "bool": {
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "tachikawa, yuji"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "tachikawa, yuji"
                      }
                    }
                  ]
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.full_name": "tachikawa, yuji"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_author_colon_bai():
    query = IQ('author:Y.Nomura.1')

    expected = {
        "bool": {
            "should": [
              {
                "match": {
                  "authors.name_variations": "Y.Nomura.1"
                }
              },
              {
                "match": {
                  "authors.full_name": "Y.Nomura.1"
                }
              },
              {
                "match": {
                  "authors.inspire_bai": "Y.Nomura.1"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_author_colon_bai_and_collection_colon():
    query = IQ(
        'author:E.Witten.1 AND collection:citeable')

    expected = {
        "bool": {
            "should": [
              {
                "match": {
                  "authors.name_variations": "E.Witten.1"
                }
              },
              {
                "match": {
                  "authors.full_name": "E.Witten.1"
                }
              },
              {
                "match": {
                  "authors.inspire_bai": "E.Witten.1"
                }
              }
            ],
            "must": [
              {
                "multi_match": {
                  "query": "citeable",
                  "fields": [
                    "collections.primary"
                  ]
                }
              }
            ]
        }
    }
    result = query.to_dict()
    assert expected == result


def test_author_colon_bai_with_double_quotes_and_collection_colon():
    query = IQ('author:"E.Witten.1" AND collection:citeable')

    expected = {
        "bool": {
            "should": [
              {
                "match": {
                  "authors.full_name": "E.Witten.1"
                }
              }
            ],
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "E.Witten.1"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "E.Witten.1"
                      }
                    }
                  ]
                }
              },
              {
                "multi_match": {
                  "query": "citeable",
                  "fields": [
                    "collections.primary"
                  ]
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_author_colon_bai_and_collection_colon_and_cited_colon():
    query = IQ(
        'author:E.Witten.1 AND collection:citeable AND cited:500->1000000')

    expected = {
        "bool": {
            "must": [
              {
                "multi_match": {
                  "query": "citeable",
                  "fields": [
                    "collections.primary"
                  ]
                }
              },
              {
                "range": {
                  "citation_count": {
                    "gte": "500",
                    "lte": "1000000"
                  }
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.name_variations": "E.Witten.1"
                }
              },
              {
                "match": {
                  "authors.full_name": "E.Witten.1"
                }
              },
              {
                "match": {
                  "authors.inspire_bai": "E.Witten.1"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_author_colon_bai_with_double_quotes_and_collection_colon_and_cited_colon():
    query = IQ(
        'author:"E.Witten.1" AND collection:citeable AND cited:500->1000000')

    expected = {
        "bool": {
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "E.Witten.1"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "E.Witten.1"
                      }
                    }
                  ]
                }
              },
              {
                "multi_match": {
                  "query": "citeable",
                  "fields": [
                    "collections.primary"
                  ]
                }
              },
              {
                "range": {
                  "citation_count": {
                    "gte": "500",
                    "lte": "1000000"
                  }
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.full_name": "E.Witten.1"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_colon_or_eprint_without_keyword():
    query = IQ('author:"Takayanagi, Tadashi" or hep-th/0010101')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_author_colon_or_author_colon_or_title_colon_or_title_colon():
    query = IQ(
        "(author:'Hiroshi Okada' OR (author:'H Okada' hep-ph) OR "
        "title: 'Dark matter in supersymmetric U(1(B-L) model' OR "
        "title: 'Non-Abelian discrete symmetry for flavors')")

    expected = {
        'bool': {
            'should': [
                {
                    'bool': {
                        'should': [
                            {
                                'bool': {
                                    'should': [
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
                                        },
                                        {
                                            'multi_match': {
                                                'query': 'Hiroshi Okada',
                                                'type': 'phrase',
                                                'fields': [
                                                    'authors.full_name',
                                                    'authors.alternative_name'
                                                ],
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
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_citedby_colon():
    query = IQ('citedby:foobar')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_citedby_colon_recid_colon():
    query = IQ('citedby:recid:902780')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_eprint_colon_with_arxiv():
    query = IQ('eprint:arxiv:TODO')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_eprint_colon_without_arxiv():
    query = IQ('eprint:TODO')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor_colon():
    query = IQ('ea:matt visser')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor_colon_and_collection_colon():
    query = IQ('ea: matt visser AND collection:citeable')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_exactauthor_colon_bai():
    query = IQ('exactauthor:J.Serra.3')

    expected = {
        "multi_match": {
            "query": "J.Serra.3",
            "fields": [
              "exactauthor.raw",
              "authors.full_name",
              "authors.alternative_name",
              "authors.inspire_bai"
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_field_code_colon():
    query = IQ('fc: a')

    expected = {'multi_match': {'query': 'a', 'fields': ['field_code']}}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_or_of_exactauthor_colon_queries():
    query = IQ('exactauthor:X.Yin.1 or exactauthor:"Yin, Xi"')

    expected = {
        "multi_match": {
            "query": "J.Serra.3",
            "fields": [
              "exactauthor.raw",
              "authors.full_name",
              "authors.alternative_name",
              "authors.inspire_bai"
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_fulltext_colon():
    query = IQ('fulltext:TODO')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_journal_colon():
    query = IQ('journal:TODO')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_refersto_colon_recid_colon():
    query = IQ('refersto:recid:1286113')

    expected = {
        'multi_match': {
            'query': '1286113',
            'fields': [
                'references.recid'
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_topcite_colon():
    query = IQ('topcite:200+')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_type_code_colon():
    query = IQ('tc: l')

    expected = {'multi_match': {'query': 'l', 'fields': ['collection']}}
    result = query.to_dict()

    assert expected == result


def test_find_author_with_hash_wildcard():
    query = IQ('find a chkv#')

    expected = {
        'bool': {
            'should': [{
                'query_string': {
                    'analyze_wildcard': True,
                    'default_field': 'authors.full_name',
                    'query': 'chkv*'}}, {
                'query_string': {
                    'analyze_wildcard': True,
                    'default_field': 'authors.alternative_name',
                    'query': 'chkv*'}}
            ]}
        }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #1235')
def test_find_journal():
    query = IQ('find j "Phys.Rev.Lett.,105*"')

    expected = {
        'query_string': {
            'query': '"Phys.Rev.Lett.,105*"',
            'default_field': 'publication_info.pubnote',
            'analyze_wildcard': True
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_exactauthor():
    query = IQ('find ea witten, edward')

    expected = {
        "multi_match": {
            "query": "witten, edward",
            "fields": [
              "exactauthor.raw",
              "authors.full_name",
              "authors.alternative_name",
              "authors.inspire_bai"
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_exactauthor_not_affiliation_uppercase():
    query = IQ(
        'FIND EA RINALDI, MASSIMILIANO NOT AFF SINCROTRONE TRIESTE')

    expected = {
        "bool": {
            "must_not": [
              {
                "multi_match": {
                  "query": "SINCROTRONE TRIESTE",
                  "fields": [
                    "authors.affiliations.value",
                    "corporate_author"
                  ]
                }
              }
            ],
            "must": [
              {
                "multi_match": {
                  "query": "RINALDI, MASSIMILIANO",
                  "fields": [
                    "exactauthor.raw",
                    "authors.full_name",
                    "authors.alternative_name",
                    "authors.inspire_bai"
                  ]
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_author():
    query = IQ('find a polchinski')

    expected = {
        "bool": {
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "polchinski"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "polchinski"
                      }
                    }
                  ]
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.full_name": "polchinski"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_author_uppercase():
    query = IQ('FIND A W F CHANG')

    expected = {
        "bool": {
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "W F CHANG"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "W F CHANG"
                      }
                    }
                  ]
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.full_name": "W F CHANG"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_author_and_date():
    query = IQ('find a hatta and date after 2000')

    expected = {
        "bool": {
            "minimum_should_match": 0,
            "should": [
              {
                "match": {
                  "authors.full_name": "hatta"
                }
              }
            ],
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "hatta"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "hatta"
                      }
                    }
                  ]
                }
              },
              {
                "bool": {
                  "minimum_should_match": 1,
                  "should": [
                    {
                      "bool": {
                        "should": [
                          {
                            "bool": {
                              "should": [
                                {
                                  "range": {
                                    "imprints.date": {
                                      "gt": "2000"
                                    }
                                  }
                                },
                                {
                                  "range": {
                                    "preprint_date": {
                                      "gt": "2000"
                                    }
                                  }
                                }
                              ]
                            }
                          },
                          {
                            "range": {
                              "thesis.date": {
                                "gt": "2000"
                              }
                            }
                          }
                        ]
                      }
                    },
                    {
                      "range": {
                        "publication_info.year": {
                          "gt": "2000"
                        }
                      }
                    }
                  ]
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_author_or_author():
    query = IQ('find a gersdorff, g or a von gersdorff, g')

    expected = {
        "bool": {
            "should": [
              {
                "bool": {
                  "must": [
                    {
                      "bool": {
                        "should": [
                          {
                            "match": {
                              "authors.name_variations": "gersdorff, g"
                            }
                          },
                          {
                            "term": {
                              "authors.inspire_bai": "gersdorff, g"
                            }
                          }
                        ]
                      }
                    }
                  ],
                  "should": [
                    {
                      "match": {
                        "authors.full_name": "gersdorff, g"
                      }
                    }
                  ]
                }
              },
              {
                "bool": {
                  "must": [
                    {
                      "bool": {
                        "should": [
                          {
                            "match": {
                              "authors.name_variations": "von gersdorff, g"
                            }
                          },
                          {
                            "term": {
                              "authors.inspire_bai": "von gersdorff, g"
                            }
                          }
                        ]
                      }
                    }
                  ],
                  "should": [
                    {
                      "match": {
                        "authors.full_name": "von gersdorff, g"
                      }
                    }
                  ]
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_author_not_author_not_author():
    query = IQ('f a ostapchenko not olinto not haungs')

    expected = {
        "bool": {
            "minimum_should_match": 0,
            "must": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.name_variations": "ostapchenko"
                      }
                    },
                    {
                      "term": {
                        "authors.inspire_bai": "ostapchenko"
                      }
                    }
                  ]
                }
              }
            ],
            "must_not": [
              {
                "bool": {
                  "should": [
                    {
                      "match": {
                        "authors.full_name": "olinto"
                      }
                    }
                  ],
                  "must": [
                    {
                      "bool": {
                        "should": [
                          {
                            "match": {
                              "authors.name_variations": "olinto"
                            }
                          },
                          {
                            "term": {
                              "authors.inspire_bai": "olinto"
                            }
                          }
                        ]
                      }
                    }
                  ]
                }
              },
              {
                "bool": {
                  "must": [
                    {
                      "bool": {
                        "should": [
                          {
                            "match": {
                              "authors.name_variations": "haungs"
                            }
                          },
                          {
                            "term": {
                              "authors.inspire_bai": "haungs"
                            }
                          }
                        ]
                      }
                    }
                  ],
                  "should": [
                    {
                      "match": {
                        "authors.full_name": "haungs"
                      }
                    }
                  ]
                }
              }
            ],
            "should": [
              {
                "match": {
                  "authors.full_name": "ostapchenko"
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_caption():
    query = IQ('Diagram for the fermion flow violating process')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_country_code():
    query = IQ('find cc italy')

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='today must be converted to an actual date')
def test_find_date():
    query = IQ('fin date > today')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_find_field_code():
    query = IQ('find fc a')

    expected = {'multi_match': {'query': 'a', 'fields': ['field_code']}}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_report():
    query = IQ('find r atlas-conf-*')

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_find_type_code():
    query = IQ('find tc book')

    expected = {'multi_match': {'query': 'book', 'fields': ['collection']}}
    result = query.to_dict()

    assert expected == result
