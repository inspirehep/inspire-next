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

"""Tests for json convertion to orcid form."""

from inspirehep.modules.orcid.utils import convert_to_orcid

import pytest


def test_succesfull_convertion():
    record = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "abstracts": [
            {
                "source": "arXiv",
                "value": "Abstract"
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

    assert convert_to_orcid(record) == {'citation': {'citation': u'@book{Kats:2015sss,\n      author         = "Name, Full and Name2, Full",\n      title          = "{Title}",\n      eprint         = "0000.00000",\n      archivePrefix  = "arXiv",\n      primaryClass   = "hep-ph",\n      SLACcitation   = "%%CITATION = ARXIV:0000.00000;%%"\n}',
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
                                        'short-description': 'Abstract',
                                        'title': {'subtitle': 'Subtitle', 'title': 'Title3'},
                                        'type': 'REPORT'}


def test_arxiv_missing_convertion():
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
                "title": "Title2"
            },
            {
                "source": "other",
                "title": "Title3"
            }
        ]
    }

    with pytest.raises(KeyError):
        convert_to_orcid(record)
