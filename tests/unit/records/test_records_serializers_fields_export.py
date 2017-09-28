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
import pytest

from inspirehep.modules.records.serializers.fields_export import (
    get_authors_with_role,
    bibtex_document_type,
    bibtex_type_and_fields,
    get_year,
    get_journal,
    get_volume,
    get_slac_citation,
    get_report_number,
    get_type,
)


@pytest.fixture
def test_record():
    return {
        "author": [
            {"full_name": "Kiritsis, Elias",
             "inspire_roles": ["editor"]},
            {"full_name": "Nitti, Francesco",
             "inspire_roles": ["author"]},
            {"full_name": "Pimenta, Leandro Silva"},
        ],
        "document_type": ["thesis"],
        "thesis_info": {
            "degree_type": "master",
            "date": "1996-09",
        },
        "publication_info": [
            {
                "journal_title": "Rhys.Rev.",
                "year": 2018,
            },
        ],
    }


def test_get_author_by_role(test_record):
    expected = ["Nitti, Francesco", "Pimenta, Leandro Silva"]
    result = get_authors_with_role(test_record['author'], 'author')
    assert expected == result


def test_get_editor_by_role(test_record):
    expected = ["Kiritsis, Elias"]
    result = get_authors_with_role(test_record.get('author'), 'editor')
    assert expected == result


def test_bibtex_document_type(test_record):
    expected = "mastersthesis"
    result = bibtex_document_type("thesis", test_record)
    assert expected == result


def test_bibtex_document_type_prefers_article(test_record):
    input = {"thesis_info": {"degree_type": "master"}, "document_type": ["thesis", "article"]}
    expected = "article"
    result, fields = bibtex_type_and_fields(input)
    assert expected == result


def test_get_year_from_thesis_when_pubinfo_present(test_record):
    expected = "1996"
    result = get_year(test_record, 'thesis')
    assert expected == result


def test_get_journal(test_record):
    expected = "Rhys.Rev."
    result = get_journal(test_record, 'article')
    assert expected == result


def test_get_volume(test_record):
    expected = None
    result = get_volume(test_record, 'article')
    assert expected == result


def test_get_slac_citation_arxiv_old_style(test_record):
    test_data = {"arxiv_eprints": [{"value": "astro-ph/0309136"}]}
    expected = "%%CITATION = ASTRO-PH/0309136;%%"
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_slac_citation_arxiv_new_style(test_record):
    test_data = {"arxiv_eprints": [{"value": "1501.00001"}]}
    expected = "%%CITATION = ARXIV:1501.00001;%%"
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_slac_citation_only_report(test_record):
    test_data = {"report_numbers": [{"value": "CERN-SOME-REPORT"}, {"value": "CERN-SOME-OTHER-REPORT"}]}
    expected = "%%CITATION = CERN-SOME-REPORT;%%"
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_slac_citation_none(test_record):
    test_data = {"key": 123456}
    expected = None
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_report_number(test_record):
    test_data = {"report_numbers": [{"value": "CERN-SOME-REPORT"}, {"value": "CERN-SOME-OTHER-REPORT"}]}
    expected = "CERN-SOME-REPORT, CERN-SOME-OTHER-REPORT"
    result = get_report_number(test_data, 'article')
    assert expected == result


def test_get_type(test_record):
    test_data = dict(test_record)
    test_data['thesis_info']['degree_type'] = 'bachelor'
    expected = 'Bachelor thesis'
    result = get_type(test_data, 'mastersthesis')
    assert expected == result
