# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Tests for json conversion to orcid form."""

from inspirehep.modules.orcid.utils import convert_to_orcid

import pytest


def test_successfull_conversion():

    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "abstracts": [
            {
                "source": "arXiv",
                "value": "<with_html_tag>Abstract</with_html_tag>"
            }
        ],
        "arxiv_eprints": [
            {
                "categories": [
                    "hep-ph"
                ],
                "value": "arXiv:0000.00000"
            }
        ],
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Affil Inst."
                    }
                ],
                "curated_relation": False,
                "full_name": "Name, Full",
                "inspire_id": "INSPIRE-00000000",
                "orcid": "0000-0000-0000"
            },
            {
                "affiliations": [
                    {
                        "value": "Affil Inst."
                    }
                ],
                "curated_relation": False,
                "full_name": "Name2, Full",
                "inspire_id": "INSPIRE-00000001"
            }
        ],
        "collections": [
            {
                "primary": "report"
            },
            {
                "primary": "arXiv"
            },
            {
                "primary": "book"
            },
            {
                "primary": "HEP"
            }
        ],
        "publication_info": [
            {
                "journal_volume": "19",
                "journal_title": "Nuovo Cim.",
                "page_artid": "154-164",
                "year": 1961
            }
        ],
        "control_number": "0000000",
        "external_system_numbers": [
            {
                "institute": "INSPIRETeX",
                "obsolete": False,
                "value": "Kats:2015sss"
            },
            {
                "institute": "arXiv",
                "obsolete": False,
                "value": "oai:arXiv.org:0000.00000"
            }
        ],
        "public_notes": [
            {
                "source": "arXiv",
                "value": "17 pages, 3 figures"
            }
        ],
        "self": {
            "$ref": "http://localhost:5000/api/literature/0000000"
        },
        "titles": [
            {
                "source": "arXiv",
                "title": "Title",
                "subtitle": "Subtitle"
            },
            {
                "title": "Title2"
            },
            {
                "source": "other",
                "title": "Title3"
            }
        ]
    }

    expected = {'citation': {'citation': u'@book{Kats:2015sss,\n      author         = "Name, Full and Name2, Full",\n      title          = "{Title}",\n      volume         = "19",\n      year           = "1961",\n      eprint         = "0000.00000",\n      archivePrefix  = "arXiv",\n      primaryClass   = "hep-ph",\n      SLACcitation   = "%%CITATION = ARXIV:0000.00000;%%"\n}',
                             'citation-type': 'BIBTEX'},
                'contributors': {'contributor': [{'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'FIRST'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '',
                                                  'credit-name': 'Name2, Full'}]},
                'external-identifiers': {'work-external-identifier': [{'external-identifier-id': 'arXiv:0000.00000',
                                                                       'external-identifier-type': 'ARXIV'}]},
                'journal-title': 'Nuovo Cim.',
                'short-description': 'Abstract',
                'title': {'subtitle': 'Subtitle', 'title': 'Title'},
                'type': 'REPORT'}
    result = convert_to_orcid(record)
    assert expected == result


def test_arxiv_missing_conversion():
    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "abstracts": [
            {
                "source": "arXiv",
                "value": "Abstract"
            }
        ],
        "authors": [
            {
                "affiliations": [
                    {
                        "value": "Affil Inst."
                    }
                ],
                "curated_relation": False,
                "full_name": "Name, Full",
                "inspire_id": "INSPIRE-00000000",
                "orcid": "0000-0000-0000"
            },
            {
                "affiliations": [
                    {
                        "value": "Affil Inst."
                    }
                ],
                "curated_relation": False,
                "full_name": "Name2, Full",
                "inspire_id": "INSPIRE-00000001"
            }
        ],
        "collections": [
            {
                "primary": "report"
            },
            {
                "primary": "arXiv"
            },
            {
                "primary": "book"
            },
            {
                "primary": "HEP"
            }
        ],
        "control_number": "0000000",
        "external_system_numbers": [
            {
                "institute": "INSPIRETeX",
                "obsolete": False,
                "value": "Kats:2015sss"
            },
            {
                "institute": "arXiv",
                "obsolete": False,
                "value": "oai:arXiv.org:0000.00000"
            }
        ],
        "public_notes": [
            {
                "source": "arXiv",
                "value": "17 pages, 3 figures"
            }
        ],
        "self": {
            "$ref": "http://localhost:5000/api/literature/0000000"
        },
        "titles": [
            {
                "source": "arXiv",
                "title": "Title",
                "subtitle": "Subtitle"
            },
            {
                "title": ""
            },
            {
                "source": "other",
                "title": "Title3"
            }
        ]
    }

    with pytest.raises(KeyError):
        convert_to_orcid(record)


def test_record():
    record = {
        "titles": [
            {
                "title": "Title"
            }
        ],
        "dois": [
            {
                "value": "00.0000/PhysRevD.00.000000"
            }
        ],
        "publication_info": [
            {
                "year": 1961
            }
        ],
        "collections": [
            {
                "primary": "not_valid"
            }
        ],
        "control_number": "0000000",
        "imprints": [
            {
                "date": "2008-08-14"
            }
        ]
    }

    excepted = {'citation': {'citation': u'@article{,\n      key            = "0000000",\n      title          = "{Title}",\n      year           = "1961",\n      doi            = "00.0000/PhysRevD.00.000000",\n      SLACcitation   = "%%CITATION = INSPIRE-0000000;%%"\n}',
                             'citation-type': 'BIBTEX'},
                'external-identifiers': {'work-external-identifier': [{'external-identifier-id': '00.0000/PhysRevD.00.000000',
                                                                       'external-identifier-type': 'DOI'}]},
                'journal-title': None,
                'publication-date': {'day': 14, 'month': 8, 'year': 2008},
                'title': {'subtitle': '', 'title': 'Title'},
                'type': 'UNDEFINED'}
    result = convert_to_orcid(record)

    assert excepted == result


def test_record_with_more_than_20_authors_return_the_first_20_authors():
    record = {"titles": [
        {
            "title": "Title"
        }
    ],
        "authors": [{
            "affiliations": [{
                "value": "Affil Inst."
            }
            ],
            "curated_relation": False,
            "full_name": "Name, Full" + str(i),
            "inspire_id": "INSPIRE-00000000",
            "orcid": "0000-0000-0000"
        } for i in range(22)],
        "dois": [
        {
            "value": "00.0000/PhysRevD.00.000000"
        }
    ],
        "publication_info": [
        {
            "year": 1961
        }],
        "collections": [
        {
            "primary": "not_valid"
        }
    ],
        "control_number": "0000000",
        "imprints": [
        {
            "date": "2008-08-14"
        }
    ]
    }

    expected = {'citation': {'citation': u'@article{,\n      key            = "0000000",\n      author         = "Name, Full0 and others",\n      title          = "{Title}",\n      year           = "1961",\n      doi            = "00.0000/PhysRevD.00.000000",\n      SLACcitation   = "%%CITATION = INSPIRE-0000000;%%"\n}',
                             'citation-type': 'BIBTEX'},
                'contributors': {'contributor': [{'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'FIRST'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full0'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full1'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full2'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full3'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full4'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full5'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full6'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full7'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full8'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full9'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full10'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full11'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full12'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full13'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full14'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full15'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full16'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full17'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full18'},
                                                 {'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                             'contributor-sequence': 'ADDITIONAL'},
                                                  'contributor-orcid': '0000-0000-0000',
                                                  'credit-name': 'Name, Full19'}]},
                'external-identifiers': {'work-external-identifier': [{'external-identifier-id': '00.0000/PhysRevD.00.000000',
                                                                       'external-identifier-type': 'DOI'}]},
                'journal-title': None,
                'publication-date': {'day': 14, 'month': 8, 'year': 2008},
                'title': {'subtitle': '', 'title': 'Title'},
                'type': 'UNDEFINED'}
    result = convert_to_orcid(record)

    assert expected == result


def test_record_without_title():
    record = {
        "titles": [
            {
                "title": ""
            }
        ],
        "dois": [
            {
                "value": "00.0000/PhysRevD.00.000000"
            }
        ],
        "collections": [
            {
                "primary": "book"
            }
        ],
        "control_number": "0000000"
    }

    with pytest.raises(KeyError):
        convert_to_orcid(record)


def test_record_with_invalid_date():
    record = {
        "titles": [
            {
                "title": "Title"
            }
        ],
        "dois": [
            {
                "value": "00.0000/PhysRevD.00.000000"
            }
        ],
        "collections": [
            {
                "primary": "book"
            }
        ],
        "control_number": "0000000",
        "imprints": [
            {}
        ]
    }

    expected = {'citation': {'citation': u'@book{,\n      key            = "0000000",\n      title          = "{Title}",\n      doi            = "00.0000/PhysRevD.00.000000",\n      SLACcitation   = "%%CITATION = INSPIRE-0000000;%%"\n}',
                             'citation-type': 'BIBTEX'},
                'external-identifiers': {'work-external-identifier': [{'external-identifier-id': '00.0000/PhysRevD.00.000000',
                                                                       'external-identifier-type': 'DOI'}]},
                'publication-date': None,
                'title': {'subtitle': '', 'title': 'Title'},
                'type': 'BOOK'}

    result = convert_to_orcid(record)

    assert expected == result


def test_record_without_primary_collection():
    record = {
        "titles": [
            {
                "title": "Title"
            }
        ],
        "collections": [
            {
                "not_primary": "not_valid"
            }
        ],
        "control_number": "0000000",
        "dois": [
            {
                "value": "00.0000/PhysRevD.00.000000"
            }
        ]
    }
    excepted = {'citation': {'citation': u'@article{,\n      key            = "0000000",\n      title          = "{Title}",\n      doi            = "00.0000/PhysRevD.00.000000",\n      SLACcitation   = "%%CITATION = INSPIRE-0000000;%%"\n}',
                             'citation-type': 'BIBTEX'},
                'external-identifiers': {'work-external-identifier': [{'external-identifier-id': '00.0000/PhysRevD.00.000000',
                                                                       'external-identifier-type': 'DOI'}]},
                'title': {'subtitle': '', 'title': 'Title'},
                'type': None}
    result = convert_to_orcid(record)

    assert excepted == result
