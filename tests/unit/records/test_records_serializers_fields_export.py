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

from inspirehep.modules.records.serializers.fields_export import (
    get_authors_with_role,
    get_author,
    bibtex_document_type,
    make_author_list,
    MAX_AUTHORS_BEFORE_ET_AL,
    bibtex_type_and_fields,
    get_year,
    get_publication_info,
    get_journal,
    get_volume,
    get_slac_citation,
)

test_record = {
    "author": [
        {"full_name": "Kiritsis, Elias",
         "inspire_roles": ["editor"]},
        {"full_name": "Nitti, Francesco",
         "inspire_roles": ["author"]},
        {"full_name": "Pimenta, Leandro Silva"}
    ],
    "document_type": ["thesis"],
    "thesis_info": {
        "degree_type": "master",
        "date": ("1996", "09", None)
    },
    "publication_info": {
        "year": 2018,
        "journal": "Rhys.Rev."
    }
}


def test_get_author_by_role():
    expected = ["Nitti, Francesco", "Pimenta, Leandro Silva"]
    result = get_authors_with_role(test_record['author'], 'author')
    assert expected == result


def test_get_editor_by_role():
    expected = ["Kiritsis, Elias"]
    result = get_authors_with_role(test_record.get('author'), 'editor')
    assert expected == result


def test_get_author():
    expected = "Nitti, Francesco and Pimenta, Leandro Silva"
    result = get_author(test_record, 'article')
    assert expected == result


def test_bibtex_document_type():
    expected = "mastersthesis"
    result = bibtex_document_type("thesis", test_record)
    assert expected == result


def test_make_author_list_long():
    test_data = ["A, B", "C, D", "E, F", "G, H", "I, J", "K, L", "M, N", "O, P", "Q, R", "S, T", "U, V", "W, X", "Y, Z"]
    if len(test_data) > MAX_AUTHORS_BEFORE_ET_AL:
        expected = "A, B and others"
    else:
        expected = "A, B and C, D and E, F and G, H and I, J and K, L and M, N and O, P and Q, R and S, T " \
                   "and U, V and W, X and Y, Z"
    result = make_author_list(test_data)
    assert expected == result


def test_bibtex_document_type_prefers_article():
    input = {"thesis_info": {"degree_type": "master"}, "document_type": ["thesis", "article"]}
    expected = "article"
    result, fields = bibtex_type_and_fields(input)
    assert expected == result


def test_get_year_from_thesis_when_pubinfo_present():
    expected = "1996"
    result = get_year(test_record, 'mastersthesis')
    assert expected == result


def test_get_publication_info():
    expected = test_record["publication_info"]
    result = get_publication_info(test_record)
    assert expected == result


def test_get_journal():
    expected = "Rhys.Rev."
    result = get_journal(test_record, 'article')
    assert expected == result


def test_get_volume():
    expected = None
    result = get_volume(test_record, 'article')
    assert expected == result


def test_get_slac_citation_arxiv_old_style():
    test_data = {"arxiv_eprints": {"value": "hep/123456"}}
    expected = "%%CITATION = HEP/123456;%%"
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_slac_citation_arxiv_new_style():
    test_data = {"arxiv_eprints": {"value": "123.456"}}
    expected = "%%CITATION = ARXIV:123.456;%%"
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_slac_citation_only_report():
    test_data = {"reportNumber": "CERN-SOME-REPORT"}
    expected = "%%CITATION = CERN-SOME-REPORT;%%"
    result = get_slac_citation(test_data, 'article')
    assert expected == result


def test_get_slac_citation_none():
    test_data = {}
    expected = None
    result = get_slac_citation(test_data, 'article')
    assert expected == result
