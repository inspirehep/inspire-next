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
    bibtex_document_type,
    bibtex_type_and_fields,
    get_year,
    get_journal,
    get_volume,
    get_report_number,
    get_type,
    get_country_name_by_code,
    get_author,
    get_best_publication_info,
    get_note
)


def test_get_author_by_role():
    test_record = {
        "authors": [
            {"full_name": "Kiritsis, Elias",
             "inspire_roles": ["editor"]},
            {"full_name": "Nitti, Francesco",
             "inspire_roles": ["author"]},
            {"full_name": "Pimenta, Leandro Silva"},
        ]
    }
    expected = ["Nitti, Francesco", "Pimenta, Leandro Silva"]
    result = get_authors_with_role(test_record['authors'], 'author')
    assert expected == result


def test_get_editor_by_role():
    test_record = {
        "authors": [
            {"full_name": "Kiritsis, Elias",
             "inspire_roles": ["editor"]},
            {"full_name": "Nitti, Francesco",
             "inspire_roles": ["author"]}
        ]
    }
    expected = ["Kiritsis, Elias"]
    result = get_authors_with_role(test_record.get('authors'), 'editor')
    assert expected == result


def test_bibtex_document_type():
    test_record = {
        "document_type": ["thesis"],
        "thesis_info": {
            "degree_type": "master"
        }
    }
    expected = "mastersthesis"
    result = bibtex_document_type("thesis", test_record)
    assert expected == result


def test_bibtex_document_type_prefers_article():
    input = {"thesis_info": {"degree_type": "master"}, "document_type": ["thesis", "article"]}
    expected = "article"
    result, fields = bibtex_type_and_fields(input)
    assert expected == result


def test_get_year_from_thesis_when_pubinfo_present():
    test_record = {
        "thesis_info": {
            "degree_type": "master",
            "date": "1996-09",
        }
    }
    expected = 1996
    result = get_year(test_record, 'thesis')
    assert expected == result


def test_get_journal():
    test_record = {
        "publication_info": [
            {
                "journal_title": "Rhys.Rev."
            }
        ]
    }
    expected = "Rhys.Rev."
    result = get_journal(test_record, 'article')
    assert expected == result


def test_get_volume():
    test_record = {
        "publication_info": [
            {
                "journal_volume": "12"
            },
        ]
    }
    expected = '12'
    result = get_volume(test_record, 'article')
    assert expected == result


def test_get_report_number():
    test_data = {"report_numbers": [{"value": "CERN-SOME-REPORT"}, {"value": "CERN-SOME-OTHER-REPORT"}]}
    expected = "CERN-SOME-REPORT, CERN-SOME-OTHER-REPORT"
    result = get_report_number(test_data, 'article')
    assert expected == result


def test_get_type():
    test_data = {
        "document_type": ["thesis"],
        "thesis_info": {
            "degree_type": "bachelor"
        }
    }
    expected = 'Bachelor thesis'
    result = get_type(test_data, 'mastersthesis')
    assert expected == result


def test_get_country_name_by_code_existing():
    assert 'Germany' == get_country_name_by_code('DE', default='DE')


def test_get_country_name_by_code_default():
    assert 'YY' == get_country_name_by_code('XX', default='YY')


def test_get_author():
    test_record = {
        "corporate_author": ["Corp A", "Corp B"]
    }
    expected = "{Corp A} and {Corp B}"
    result = get_author(test_record, 'article')
    assert expected == result


def test_get_best_publication_info():
    test_record = {
        "publication_info": [
            {
                "journal_title": "A",
                "journal_issue": "1",
            },
            {
                "journal_title": "B",
                "journal_issue": "2",
                "journal_volume": "2",
            },
            {
                "journal_title": "C",
                "journal_issue": "3",
                "journal_volume": "3",
                "year": 2017
            }
        ]
    }
    expected = test_record['publication_info'][2]
    result = get_best_publication_info(test_record)
    assert expected == result


def test_note_on_erratum():
    test_record = {
        "publication_info": [
            {
                "journal_title": u"Zażółć gęślą jaźń",
                "journal_volume": "A",
                "page_start": "12",
                "page_end": "15",
                "year": 2016,
                "material": "erratum",
            },
            {
                "journal_title": "A Title",
                "journal_volume": "B",
                "artid": "987",
                "material": "addendum",
            }
        ]
    }
    expected = u"[Erratum: Zażółć gęślą jaźń A, 12--15 (2016), Addendum: A Title B, 987]"
    result = get_note(test_record, 'article')
    assert expected == result
