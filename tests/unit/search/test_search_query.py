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

from __future__ import absolute_import, division, print_function

import pytest

from inspirehep.modules.search import IQ, LiteratureSearch


def test_empty():
    query = IQ('', LiteratureSearch())

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
    query = IQ('kudenko', LiteratureSearch())

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
    query = IQ('sungtae cho or 1301.7261', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_google_style_and_not_collaboration():
    query = IQ("raffaele d'agnolo and not cn cms", LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author():
    query = IQ('a kondrashuk', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_bai_malformed():
    query = IQ('a r.j.hill.1', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_author_bai():
    query = IQ('find a r.j.hill.1', LiteratureSearch())

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
                        "authors.ids.value": "r.j.hill.1"
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
    query = IQ('a fileviez perez,p or p. f. perez', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_and_not_author():
    query = IQ('a espinosa,jose r and not a rodriguez espinosa', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_and_not_type_code():
    query = IQ('a nilles,h and not tc I', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def author_or_author_and_not_collaborations_and_not_title_and_not_type_code():
    query = IQ(
        'a rojo,j. or rojo-chacon,j. and not collaboration pierre auger '
        'and not collaboration auger and not t auger and tc p', LiteratureSearch())

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
    query = IQ('abstract: part*', LiteratureSearch())

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
    query = IQ('author: vagenas', LiteratureSearch())

    expected = {
          'bool': {
            'must': [
              {
                'bool': {
                  'should': [
                    {
                      'match': {
                        u'authors.name_variations': 'vagenas'
                      }
                    },
                    {
                      'term': {
                        u'authors.ids.value': 'vagenas'
                      }
                    }
                  ]
                }
              }
            ],
            'should': [
              {
                'match': {
                  u'authors.full_name': 'vagenas'
                }
              }
            ]
          }
        }
    result = query.to_dict()

    assert expected == result


def test_author_colon_with_double_quotes():
    query = IQ('author:"tachikawa, yuji"', LiteratureSearch())

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
                        "authors.ids.value": "tachikawa, yuji"
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
    query = IQ('author:Y.Nomura.1', LiteratureSearch())

    expected = {
          'bool': {
            'must': [
              {
                'bool': {
                  'should': [
                    {
                      'match': {
                        u'authors.name_variations': 'Y.Nomura.1'
                      }
                    },
                    {
                      'term': {
                        u'authors.ids.value': 'Y.Nomura.1'
                      }
                    }
                  ]
                }
              }
            ],
            'should': [
              {
                'match': {
                  u'authors.full_name': 'Y.Nomura.1'
                }
              }
            ]
          }
        }
    result = query.to_dict()

    assert expected == result


def test_author_colon_bai_and_collection_colon():
    query = IQ(
        'author:E.Witten.1 AND collection:citeable', LiteratureSearch())

    expected = {
          'bool': {
            'must': [
              {
                'bool': {
                  'should': [
                    {
                      'match': {
                        u'authors.name_variations': 'E.Witten.1'
                      }
                    },
                    {
                      'term': {
                        u'authors.ids.value': 'E.Witten.1'
                      }
                    }
                  ]
                }
              },
              {
                'multi_match': {
                  'fields': [
                    'collections.primary'
                  ],
                  'query': 'citeable'
                }
              }
            ],
            'should': [
              {
                'match': {
                  u'authors.full_name': 'E.Witten.1'
                }
              }
            ]
          }
        }
    result = query.to_dict()
    assert expected == result


def test_author_colon_bai_with_double_quotes_and_collection_colon():
    query = IQ('author:"E.Witten.1" AND collection:citeable', LiteratureSearch())

    expected = {
          'bool': {
            'must': [
              {
                'bool': {
                  'should': [
                    {
                      'match': {
                        u'authors.name_variations': 'E.Witten.1'
                      }
                    },
                    {
                      'term': {
                        u'authors.ids.value': 'E.Witten.1'
                      }
                    }
                  ]
                }
              },
              {
                'multi_match': {
                  'fields': [
                    'collections.primary'
                  ],
                  'query': 'citeable'
                }
              }
            ],
            'should': [
              {
                'match': {
                  u'authors.full_name': 'E.Witten.1'
                }
              }
            ]
          }
        }

    result = query.to_dict()

    assert expected == result


def test_author_colon_bai_and_collection_colon_and_cited_colon():
    query = IQ(
        'author:E.Witten.1 AND collection:citeable AND cited:500->1000000',
        LiteratureSearch()
        )

    expected = {
          'bool': {
            'must': [
              {
                'bool': {
                  'should': [
                    {
                      'match': {
                        u'authors.name_variations': 'E.Witten.1'
                      }
                    },
                    {
                      'term': {
                        u'authors.ids.value': 'E.Witten.1'
                      }
                    }
                  ]
                }
              },
              {
                'multi_match': {
                  'fields': [
                    'collections.primary'
                  ],
                  'query': 'citeable'
                }
              },
              {
                'range': {
                  'citation_count': {
                    'gte': '500',
                    'lte': '1000000'
                  }
                }
              }
            ],
            'should': [
              {
                'match': {
                  u'authors.full_name': 'E.Witten.1'
                }
              }
            ]
          }
        }
    result = query.to_dict()

    assert expected == result


def test_author_colon_bai_with_double_quotes_and_collection_colon_and_cited_colon():
    query = IQ(
        'author:"E.Witten.1" AND collection:citeable AND cited:500->1000000',
        LiteratureSearch()
    )

    expected = {
          'bool': {
            'must': [
              {
                'bool': {
                  'should': [
                    {
                      'match': {
                        u'authors.name_variations': 'E.Witten.1'
                      }
                    },
                    {
                      'term': {
                        u'authors.ids.value': 'E.Witten.1'
                      }
                    }
                  ]
                }
              },
              {
                'multi_match': {
                  'fields': [
                    'collections.primary'
                  ],
                  'query': 'citeable'
                }
              },
              {
                'range': {
                  'citation_count': {
                    'gte': '500',
                    'lte': '1000000'
                  }
                }
              }
            ],
            'should': [
              {
                'match': {
                  u'authors.full_name': 'E.Witten.1'
                }
              }
            ]
          }
        }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_author_colon_or_eprint_without_keyword():
    query = IQ(
        'author:"Takayanagi, Tadashi" or hep-th/0010101',
        LiteratureSearch()
    )

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_author_colon_or_author_colon_or_title_colon_or_title_colon():
    query = IQ(
        "(author:'Hiroshi Okada' OR (author:'H Okada' hep-ph) OR "
        "title: 'Dark matter in supersymmetric U(1(B-L) model' OR "
        "title: 'Non-Abelian discrete symmetry for flavors')",
        LiteratureSearch()
        )

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
                                                                'authors.alternative_names'
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
                                                    'authors.alternative_names'
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
    query = IQ('citedby:foobar', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_citedby_colon_recid_colon():
    query = IQ('citedby:recid:902780', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_eprint_colon_with_arxiv():
    query = IQ('eprint:arxiv:TODO', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_eprint_colon_without_arxiv():
    query = IQ('eprint:TODO', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor_colon():
    query = IQ('ea:matt visser', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='query is malformed, but user intent is clear')
def test_exactauthor_colon_and_collection_colon():
    query = IQ('ea: matt visser AND collection:citeable', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_exactauthor_colon_bai():
    query = IQ('exactauthor:J.Serra.3', LiteratureSearch())

    expected = {
        "multi_match": {
            "query": "J.Serra.3",
            "fields": [
              "exactauthor.raw",
              "authors.full_name",
              "authors.alternative_names",
              "authors.ids.value"
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_field_code_colon():
    query = IQ('fc: a', LiteratureSearch())

    expected = {'multi_match': {'query': 'a', 'fields': ['field_code']}}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='BAI is not part of the mappings')
def test_or_of_exactauthor_colon_queries():
    query = IQ('exactauthor:X.Yin.1 or exactauthor:"Yin, Xi"', LiteratureSearch())

    expected = {
        "multi_match": {
            "query": "J.Serra.3",
            "fields": [
              "exactauthor.raw",
              "authors.full_name",
              "authors.alternative_names",
              "authors.ids.value"
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_fulltext_colon():
    query = IQ('fulltext:TODO', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_journal_colon():
    query = IQ('journal:TODO', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_refersto_colon_recid_colon():
    query = IQ('refersto:recid:1286113', LiteratureSearch())

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
    query = IQ('topcite:200+', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_type_code_colon():
    query = IQ('tc: l', LiteratureSearch())

    expected = {'multi_match': {'query': 'l', 'fields': ['collection']}}
    result = query.to_dict()

    assert expected == result


def test_find_author_with_hash_wildcard():
    query = IQ('find a chkv#', LiteratureSearch())

    expected = {
        'bool': {
            'should': [{
                'query_string': {
                    'analyze_wildcard': True,
                    'default_field': 'authors.full_name',
                    'query': 'chkv*'}}, {
                'query_string': {
                    'analyze_wildcard': True,
                    'default_field': 'authors.alternative_names',
                    'query': 'chkv*'}}
            ]}
        }
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #1235')
def test_find_journal():
    query = IQ('find j "Phys.Rev.Lett.,105*"', LiteratureSearch())

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
    query = IQ('find ea witten, edward', LiteratureSearch())

    expected = {
        "multi_match": {
            "query": "witten, edward",
            "fields": [
              "exactauthor.raw",
              "authors.full_name",
              "authors.alternative_names",
              "authors.ids.value"
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_exactauthor_not_affiliation_uppercase():
    query = IQ(
        'FIND EA RINALDI, MASSIMILIANO NOT AFF SINCROTRONE TRIESTE', LiteratureSearch())

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
                    "authors.alternative_names",
                    "authors.ids.value"
                  ]
                }
              }
            ]
        }
    }
    result = query.to_dict()

    assert expected == result


def test_find_author():
    query = IQ('find a polchinski', LiteratureSearch())

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
                        "authors.ids.value": "polchinski"
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
    query = IQ('FIND A W F CHANG', LiteratureSearch())

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
                        "authors.ids.value": "W F CHANG"
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
    query = IQ('find a hatta and date after 2000', LiteratureSearch())

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
                        "authors.ids.value": "hatta"
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
    query = IQ('find a gersdorff, g or a von gersdorff, g', LiteratureSearch())

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
                              "authors.ids.value": "gersdorff, g"
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
                              "authors.ids.value": "von gersdorff, g"
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
    query = IQ('f a ostapchenko not olinto not haungs', LiteratureSearch())

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
                        "authors.ids.value": "ostapchenko"
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
                              "authors.ids.value": "olinto"
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
                              "authors.ids.value": "haungs"
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
    query = IQ('Diagram for the fermion flow violating process', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_country_code():
    query = IQ('find cc italy', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='today must be converted to an actual date')
def test_find_date():
    query = IQ('fin date > today', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_find_field_code():
    query = IQ('find fc a', LiteratureSearch())

    expected = {'multi_match': {'query': 'a', 'fields': ['field_code']}}
    result = query.to_dict()

    assert expected == result


@pytest.mark.xfail(reason='tracked in issue #817')
def test_find_report():
    query = IQ('find r atlas-conf-*', LiteratureSearch())

    expected = {}
    result = query.to_dict()

    assert expected == result


def test_find_type_code():
    query = IQ('find tc book', LiteratureSearch())

    expected = {'multi_match': {'query': 'book', 'fields': ['collection']}}
    result = query.to_dict()

    assert expected == result
