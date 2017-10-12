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

from inspirehep.utils.record_getter import get_es_record
from inspirehep.modules.orcid import OrcidConverter
from flask import current_app


def test_format_article(app):
    article = get_es_record('lit', 4328)
    expected = {
        'title': {
            'title': {
                'value': u'Partial Symmetries of Weak Interactions'
            }
        },
        'journal-title': {
            'value': u'Nucl.Phys.'
        },
        'type': 'journal-article',
        'publication-date': {
            'year': {
                'value': '1961'
            }
        },
        'external-ids': {
            'external-id': [
                {
                    'external-id-type': 'doi',
                    'external-id-value': u'10.1016/0029-5582(61)90469-2',
                    'external-id-url': {
                        'value': 'http://dx.doi.org/10.1016/0029-5582(61)90469-2'
                    },
                    'external-id-relationship': 'self'
                }
            ]
        },
        'url': {
            'value': 'http://{}/record/4328'.format(current_app.config['SERVER_NAME'])
        },
        'contributors': {
            'contributor': [
                {
                    'credit-name': {
                        'value': u'Glashow, S.L.'
                    },
                    'contributor-attributes': {
                        'contributor-sequence': 'first',
                        'contributor-role': 'author'
                    }
                }
            ]
        },
        'visibility': 'public'
    }

    result = OrcidConverter(article).get_json()
    assert result == expected


def test_format_conference_paper(app):
    inproceedings = get_es_record('lit', 524480)
    expected = {
        'contributors': {
            'contributor': [
                {
                    'contributor-attributes': {
                        'contributor-role': 'author',
                        'contributor-sequence': 'first'
                    },
                    'credit-name': {
                        'value': u'Hu, Wayne'
                    }
                }
            ]
        },
        'external-ids': {
            'external-id': [
                {
                    'external-id-relationship': 'self',
                    'external-id-type': 'arxiv',
                    'external-id-url': {
                        'value': 'http://arxiv.org/abs/astro-ph/0002520'
                    },
                    'external-id-value': u'astro-ph/0002520'
                }
            ]
        },
        'journal-title': {
            'value': u'4th RESCEU International Symposium on Birth and Evolution of the Universe'
        },
        'title': {
            'title': {
                'value': u'CMB anisotropies: A Decadal survey'
            }
        },
        'type': 'conference-paper',
        'url': {
            'value': 'http://{}/record/524480'.format(current_app.config['SERVER_NAME'])
        },
        'visibility': 'public'
    }

    result = OrcidConverter(inproceedings).get_json()
    assert result == expected


def test_format_proceedings(app):
    proceedings = get_es_record('lit', 701585)
    expected = {
        'contributors': {
            'contributor': [
                {
                    'contributor-attributes': {
                        'contributor-role': 'editor',
                        'contributor-sequence': 'first'
                    },
                    'credit-name': {
                        'value': u'De Roeck, A.'
                    }
                },
                {
                    'contributor-attributes': {
                        'contributor-role': 'editor',
                        'contributor-sequence': 'additional'
                    },
                    'credit-name': {
                        'value': u'Jung, H.'
                    }
                }
            ]
        },
        'external-ids': {
            'external-id': [
                {
                    'external-id-relationship': 'self',
                    'external-id-type': 'arxiv',
                    'external-id-url': {
                        'value': 'http://arxiv.org/abs/hep-ph/0601012'
                    },
                    'external-id-value': u'hep-ph/0601012'
                }
            ]
        },
        'publication-date': {
            'media-type': 'print',
            'year': {
                'value': '2005'
            }
        },
        'title': {
            'title': {
                'value': u'HERA and the LHC: A Workshop on the implications of HERA for LHC physics: Proceedings Part A'
            }
        },
        'type': 'conference-abstract',
        'url': {
            'value': 'http://localhost:5000/record/701585'
        },
        'visibility': 'public'
    }

    result = OrcidConverter(proceedings).get_json()
    assert result == expected


def test_format_thesis(app):
    phdthesis = get_es_record('lit', 1395663)
    expected = {
        'contributors': {
            'contributor': [
                {
                    'contributor-attributes': {
                        'contributor-role': 'author',
                        'contributor-sequence': 'first'
                    },
                    'credit-name': {
                        'value': u'Mankuzhiyil, Nijil'
                    }
                },
                {
                    'contributor-attributes': {
                        'contributor-role': 'support-staff',
                        'contributor-sequence': 'additional'
                    },
                    'credit-name': {
                        'value': u'de Angelis, Alessandro'
                    }
                }
            ]
        },
        'title': {
            'title': {
                'value': u'MAGIC $\\gamma$-ray observations of distant AGN and a study of source variability and the extragalactic background light using FERMI and air Cherenkov telescopes'
            }
        },
        'type': 'dissertation',
        'url': {
            'value': 'http://localhost:5000/record/1395663'
        },
        'visibility': 'public'
    }

    result = OrcidConverter(phdthesis).get_json()
    assert result == expected


def test_format_book(app):
    book = get_es_record('lit', 736770)
    expected = {
        'contributors': {
            'contributor': [
                {
                    'contributor-attributes': {
                        'contributor-role': 'author',
                        'contributor-sequence': 'first'
                    },
                    'credit-name': {
                        'value': u'Fecko, M.'
                    }
                }
            ]
        },
        'external-ids': {
            'external-id': [
                {
                    'external-id-type': 'isbn',
                    'external-id-value': u'9780521187961'
                },
                {
                    'external-id-type': 'isbn',
                    'external-id-value': u'9780521845076'
                },
                {
                    'external-id-type': 'isbn',
                    'external-id-value': u'9780511242960'
                }
            ]
        },
        'publication-date': {
            'media-type': 'print',
            'year': {
                'value': '2011'
            },
            'month': {
                'value': '03'
            },
            'day': {
                'value': '03'
            }
        },
        'title': {
            'title': {
                'value': u'Differential geometry and Lie groups for physicists'
            }
        },
        'type': 'book',
        'url': {
            'value': 'http://localhost:5000/record/736770'
        },
        'visibility': 'public'
    }

    result = OrcidConverter(book).get_json()
    assert result == expected


def test_format_book_chapter(app):
    inbook = get_es_record('lit', 1375491)
    expected = {
        'contributors': {
            'contributor': [
                {
                    'contributor-attributes': {
                        'contributor-role': 'author',
                        'contributor-sequence': 'first'
                    },
                    'credit-name': {
                        'value': u'Bechtle, Philip'
                    }
                },
                {
                    'contributor-attributes': {
                        'contributor-role': 'author',
                        'contributor-sequence': 'additional'
                    },
                    'credit-name': {
                        'value': u'Plehn, Tilman'
                    }
                },
                {
                    'contributor-attributes': {
                        'contributor-role': 'author',
                        'contributor-sequence': 'additional'
                    },
                    'credit-name': {
                        'value': u'Sander, Christian'
                    }
                }
            ]
        },
        'external-ids': {
            'external-id': [
                {
                    'external-id-relationship': 'self',
                    'external-id-type': 'doi',
                    'external-id-url': {
                        'value': 'http://dx.doi.org/10.1007/978-3-319-15001-7_10'
                    },
                    'external-id-value': u'10.1007/978-3-319-15001-7_10'
                },
                {
                    'external-id-relationship': 'self',
                    'external-id-type': 'arxiv',
                    'external-id-url': {
                        'value': 'http://arxiv.org/abs/1506.03091'
                    },
                    'external-id-value': u'1506.03091'
                }
            ]
        },
        'publication-date': {
            'year': {
                'value': '2015'
            }
        },
        'title': {
            'title': {
                'value': u'Supersymmetry'
            }
        },
        'type': 'book-chapter',
        'url': {
            'value': 'http://localhost:5000/record/1375491'
        },
        'visibility': 'public'
    }

    result = OrcidConverter(inbook).get_json()
    assert result == expected
