# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from factories.db.invenio_records import TestRecordMetadata
from freezegun import freeze_time
from textwrap import dedent


def test_latex_serializer_serialize_EU(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Ditko, Steve',
            },
            {
                'full_name': 'Lieber, Larry'
            }
        ],
        'collaborations': [
            {
                'value': 'LHCb',
            },
            {
                'value': 'Marvel',
            },
            {
                'value': 'Comics',
            }
        ],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'page_start': '500',
            'page_end': '593',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee \\textit{et al.} [LHCb, Marvel and Comics],
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58} (2014) no.120, 500-593
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_latex_serializer_serialize_US(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Ditko, Steve',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'page_start': '500',
            'page_end': '593',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.us+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee \\textit{et al.} [LHCb],
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58}, no.120, 500-593 (2014)
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_uses_artid_when_there_is_no_page_range_EU(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Ditko, Steve',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'page_end': '500',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee \\textit{et al.} [LHCb],
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58} (2014) no.120, 17920
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_uses_page_start_as_page_range_EU(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Ditko, Steve',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'page_start': '500',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee \\textit{et al.} [LHCb],
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58} (2014) no.120, 500
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_uses_artid_when_there_is_no_page_range_US(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Ditko, Steve',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'page_end': '593',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.us+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee \\textit{et al.} [LHCb],
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58}, no.120, 17920 (2014)
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_without_collaborations_page_range_and_artid(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Ditko, Steve',
            },
        ],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee and S.~Ditko,
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58} (2014) no.120
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_with_one_author(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'journal_issue': '120',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee [LHCb],
    %``The Amazing Spiderman,''
    Phys.\\ Rev.\\ A \\textbf{58} (2014) no.120, 17920
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_with_multiple_authors(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Astonishing Ant-man',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
            {
                'full_name': 'Kirby, Jack',
            },
            {
                'full_name': 'Lieber, Larry'
            }
        ],
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee, J.~Kirby and L.~Lieber,
    %``The Astonishing Ant-man,''"""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_uses_report_number_without_doi_and_arxiv_eprint(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'Physics',
            },
        ],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]

    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    %``Physics,''
    DESY-17-036."""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_with_collaborations_and_no_authors(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'Physics',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }]

    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
     [LHCb],
    %``Physics,''"""
    result = response.data

    assert dedent(expected) == result


def test_jinja_template_does_not_print_incomplete_publication_info(isolated_api_client):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'control_number': '64209',
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'The Amazing Spiderman',
            },
        ],
        'authors': [
            {
                'full_name': 'Lee, Stan',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_volume': '58',
            'journal_issue': '120',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    TestRecordMetadata.create_from_kwargs(
        json=record_json, index_name='records-hep')
    response = isolated_api_client.get(
        '/literature/64209',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{a123bx}
    \\bibitem{a123bx}
    S.~Lee [LHCb],
    %``The Amazing Spiderman,''
    doi:10.1088/1361-6633/aa5514
    [arXiv:1607.06746 [hep-th]]."""
    result = response.data

    assert dedent(expected) == result


@freeze_time("1994-12-19")
def test_jinja_template_prints_citation_count(isolated_api_client):
    record_json = {
        'control_number': 321,
        'titles': [
            {
                'title': 'The Invincible Ironman',
            },
        ],
    }
    record_1 = TestRecordMetadata.create_from_kwargs(json=record_json).inspire_record

    ref = {'control_number': 4321, 'references': [{'record': {'$ref': record_1._get_ref()}}]}
    TestRecordMetadata.create_from_kwargs(json=ref)

    response = isolated_api_client.get(
        '/literature/321',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'}
    )

    expected = """\
    %\\cite{321}
    \\bibitem{321}
    %``The Invincible Ironman,''
    %1 citations counted in INSPIRE as of 19 Dec 1994"""
    result = response.data

    assert dedent(expected) == result


def xtest_latex_serializer_serialize_search_results_eu(api_client):
    response = api_client.get(
        '/literature/?q=title collider',
        headers={'Accept': 'application/vnd+inspire.latex.eu+x-latex'},
    )

    assert response.status_code == 200

    result = response.data
    expected = """\
    %\\cite{1373790}
    \\bibitem{1373790}
    T.~Sch\xc3\xb6rner-Sadenius,
    %``The Large Hadron Collider,''
    doi:10.1007/978-3-319-15001-7

    %\\cite{701585}
    \\bibitem{701585}
    A.~De Roeck and H.~Jung,
    %``HERA and the LHC: A Workshop on the implications of HERA for LHC physics: Proceedings Part A,''
    [arXiv:hep-ph/0601012 [hep-ph]]."""

    assert dedent(expected) == result


def xtest_latex_serializer_serialize_search_results_us(api_client):
    response = api_client.get(
        '/literature/?q=title collider',
        headers={'Accept': 'application/vnd+inspire.latex.us+x-latex'},
    )

    assert response.status_code == 200

    result = response.data
    expected = """\
    %\\cite{1373790}
    \\bibitem{1373790}
    T.~Sch\xc3\xb6rner-Sadenius,
    %``The Large Hadron Collider,''
    doi:10.1007/978-3-319-15001-7

    %\\cite{701585}
    \\bibitem{701585}
    A.~De Roeck and H.~Jung,
    %``HERA and the LHC: A Workshop on the implications of HERA for LHC physics: Proceedings Part A,''
    [arXiv:hep-ph/0601012 [hep-ph]]."""

    assert dedent(expected) == result
