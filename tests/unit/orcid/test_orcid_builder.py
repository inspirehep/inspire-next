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

from inspire_utils.date import PartialDate
from inspirehep.modules.orcid import OrcidBuilder


def test_add_author():
    expected = {
        "contributors": {
            "contributor": [
                {
                    "contributor-orcid": {
                        "uri": "http://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "credit-name": {
                        "value": "Josiah Carberry"
                    },
                    "contributor-email": {
                        "value": "j.carberry@orcid.org"
                    },
                    "contributor-attributes": {
                        "contributor-sequence": "first",
                        "contributor-role": "author",
                    },
                }
            ]
        }
    }

    builder = OrcidBuilder()
    builder.add_contributor("Josiah Carberry", "author", "0000-0002-1825-0097", "j.carberry@orcid.org")
    result = builder.get_json()

    assert result == expected


def test_add_multiple_authors():
    expected = {
        "contributors": {
            "contributor": [
                {
                    "contributor-orcid": {
                        "uri": "http://orcid.org/0000-0002-1825-0097",
                        "path": "0000-0002-1825-0097",
                        "host": "orcid.org",
                    },
                    "credit-name": {
                        "value": "Josiah Carberry"
                    },
                    "contributor-email": {
                        "value": "j.carberry@orcid.org"
                    },
                    "contributor-attributes": {
                        "contributor-sequence": "first",
                        "contributor-role": "author",
                    },
                },
                {
                    "credit-name": {
                        "value": "Homer Simpson"
                    },
                    "contributor-attributes": {
                        "contributor-sequence": "additional",
                        "contributor-role": "author",
                    },
                },
            ]
        }
    }

    builder = OrcidBuilder()
    builder.add_contributor("Josiah Carberry", "author", "0000-0002-1825-0097", "j.carberry@orcid.org")
    builder.add_contributor("Homer Simpson", "author")
    result = builder.get_json()

    assert result == expected


def test_set_title():
    expected = {
        "title": {
            "title": {
                "value": "Developing Thin Clients Using Amphibious Epistemologies"
            },
            "subtitle": {
                "value": "Made-up subtitle"
            },
        }
    }

    builder = OrcidBuilder()
    builder.set_title("Developing Thin Clients Using Amphibious Epistemologies", "Made-up subtitle")
    result = builder.get_json()

    assert result == expected


def test_set_publication_date():
    expected = {
        "publication-date": {
            "year": {
                "value": "1996"
            },
            "month": {
                "value": "09"
            },
            "day": {
                "value": "07"
            },
            "media-type": "print",
        }
    }

    builder = OrcidBuilder()
    builder.set_publication_date(PartialDate(1996, 9, 7), "print")
    result = builder.get_json()

    assert result == expected


def test_set_type():
    expected = {
        "type": "conference-paper"
    }

    builder = OrcidBuilder()
    builder.set_type("conference-paper")
    result = builder.get_json()

    assert result == expected


def test_add_citation():
    expected = {
        "citation": {
            "citation-type": "bibtex",
            "citation-value": "@article{...}",
        }
    }

    builder = OrcidBuilder()
    builder.set_citation("bibtex", "@article{...}")
    result = builder.get_json()

    assert result == expected


def test_source():
    source = {
        "source-orcid": {
            "uri": "https://example.org/0000-0000-0000-0000",
            "path": "0000-0000-0000-0000",
            "host": "example.org",
        }
    }
    expected = {
        "source": source
    }

    builder = OrcidBuilder(source)
    result = builder.get_json()

    assert result == expected


def test_set_country_code():
    expected = {
        "country": {
            "value": "CH"
        }
    }

    builder = OrcidBuilder()
    builder.set_country("CH")
    result = builder.get_json()

    assert result == expected


def test_add_external_id():
    expected = {
        "external-ids": {
            "external-id": [
                {
                    "external-id-type": "doi",
                    "external-id-value": "10.5555/12345679",
                    "external-id-url": {
                        "value": "http://dx.doi.org/10.5555/12345679"
                    },
                    "external-id-relationship": "self",
                }
            ]
        }
    }

    builder = OrcidBuilder()
    builder.add_external_id("doi", "10.5555/12345679", "http://dx.doi.org/10.5555/12345679", "self")
    result = builder.get_json()

    assert result == expected


def test_add_multiple_external_ids():
    expected = {
        "external-ids": {
            "external-id": [
                {
                    "external-id-type": "doi",
                    "external-id-value": "10.5555/12345679",
                    "external-id-url": {
                        "value": "http://dx.doi.org/10.5555/12345679"
                    },
                    "external-id-relationship": "self",
                },
                {
                    "external-id-type": "issn",
                    "external-id-value": "0264-3561",
                    "external-id-relationship": "part-of",
                }
            ]
        }
    }

    builder = OrcidBuilder()
    builder.add_doi("10.5555/12345679", "self")
    builder.add_external_id("issn", "0264-3561", relationship="part-of")
    result = builder.get_json()

    assert result == expected


def test_set_journal_title():
    expected = {
        "journal-title": {
            "value": "JHEP"
        }
    }

    builder = OrcidBuilder()
    builder.set_journal_title("JHEP")
    result = builder.get_json()

    assert result == expected


def test_set_title_translation():
    expected = {
        "title": {
            "title": {
                "value": "Developing Thin Clients Using Amphibious Epistemologies"
            },
            "translated-title": {
                "value": "Desarrollo de clientes ligeros que utilizan epistemologías anfibias",
                "language-code": "es"
            },
        }
    }

    builder = OrcidBuilder()
    builder.set_title("Developing Thin Clients Using Amphibious Epistemologies",
                      translated_title=("Desarrollo de clientes ligeros que utilizan epistemologías anfibias", "es"))
    result = builder.get_json()

    assert result == expected


def test_set_url():
    expected = {
        "url": {
            "value": "http://example.org"
        }
    }

    builder = OrcidBuilder()
    builder.set_url("http://example.org")
    result = builder.get_json()

    assert result == expected


def test_set_visibility():
    expected = {
        "visibility": "public"
    }

    builder = OrcidBuilder()
    builder.set_visibility("public")
    result = builder.get_json()

    assert result == expected
