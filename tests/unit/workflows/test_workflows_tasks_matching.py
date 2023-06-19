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
import requests_mock
from inspire_schemas.api import load_schema, validate
from inspire_utils.record import get_value
from mock import patch
from mocks import MockEng, MockObj

from inspirehep.modules.workflows.tasks.matching import (
    exact_match, fuzzy_match, has_fully_harvested_category,
    is_fuzzy_match_approved, pending_in_holding_pen,
    physics_data_an_is_primary_category, set_core_in_extra_data,
    set_exact_match_as_approved_in_extradata,
    set_fuzzy_match_approved_in_extradata)
from inspirehep.modules.workflows.utils import \
    _get_headers_for_hep_root_table_request


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_exact_match_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{"_source": {"control_number": 4328}}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": [4328]},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        assert exact_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [4328]
        result = get_value(obj.extra_data, "matches.exact")

        assert expected == result


def test_set_exact_match_as_approved_in_extradata():
    data = {}
    extra_data = {"matches": {"exact": [1, 2]}}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    set_exact_match_as_approved_in_extradata(obj, eng)

    assert get_value(obj.extra_data, "matches.approved") == 1


def test_set_exact_match_as_approved_in_extradata_with_empty_list_raises_exception():
    data = {}
    extra_data = {"matches": {"exact": []}}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with pytest.raises(IndexError):
        set_exact_match_as_approved_in_extradata(obj, eng)


def test_set_exact_match_as_approved_in_extradata_no_exact_key_raises_exception():
    data = {}
    extra_data = {"matches": {"wrongkey": [1]}}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with pytest.raises(KeyError):
        set_exact_match_as_approved_in_extradata(obj, eng)


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_exact_match_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/exact-match",
            json={"matched_ids": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        assert not exact_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = []
        result = get_value(obj.extra_data, "matches.exact")

        assert expected == result


def test_has_fully_harvested_category_is_true_with_core_categories(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {"core": ["hep-ph"], "non-core": ["astro-ph.CO", "gr-qc"]}
    }

    with patch.dict(app.config, categories_config):
        record = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "hep-ph",
                        "astro-ph.CO",
                        "gr-qc",
                    ],
                    "value": "1609.03939",
                },
            ],
        }
        assert validate(record["arxiv_eprints"], subschema) is None
        assert has_fully_harvested_category(record)


def test_has_fully_harvested_category_is_true_with_non_core_categories(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {"core": ["hep-ph"], "non-core": ["astro-ph.CO", "gr-qc"]}
    }

    with patch.dict(app.config, categories_config):
        record = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "astro-ph.CO",
                        "gr-qc",
                    ],
                    "value": "1609.03939",
                },
            ],
        }
        assert validate(record["arxiv_eprints"], subschema) is None
        assert has_fully_harvested_category(record)


def test_has_fully_harvested_category_is_false_with_others_categories(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {"core": ["hep-ph"], "non-core": ["astro-ph.CO", "gr-qc"]}
    }

    with patch.dict(app.config, categories_config):
        record = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "math",
                    ],
                    "value": "1609.03939",
                },
            ],
        }
        assert validate(record["arxiv_eprints"], subschema) is None
        assert not has_fully_harvested_category(record)


def physics_data_an_is_primary_category_is_false(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]
    record = {
        "arxiv_eprints": [
            {
                "categories": [
                    "math",
                ],
                "value": "1609.03939",
            },
        ],
    }
    assert validate(record["arxiv_eprints"], subschema) is None
    assert not physics_data_an_is_primary_category(record)


def physics_data_an_is_primary_category_is_true(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]
    record = {
        "arxiv_eprints": [
            {
                "categories": [
                    "physics.data-an",
                ],
                "value": "1609.03939",
            },
        ],
    }
    assert validate(record["arxiv_eprints"], subschema) is None
    assert physics_data_an_is_primary_category(record)


def test_core_is_written_in_extradata_if_article_is_core(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {"core": ["hep-ph"], "non-core": ["astro-ph.CO", "gr-qc"]}
    }

    with patch.dict(app.config, categories_config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        obj.data = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "hep-ph",
                    ],
                    "value": "1705.01122",
                },
            ],
        }
        assert validate(obj.data["arxiv_eprints"], subschema) is None
        set_core_in_extra_data(obj, eng)
        assert obj.extra_data["core"]


def test_core_is_not_written_in_extradata_if_article_is_non_core(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {"core": ["hep-ph"], "non-core": ["astro-ph.CO", "gr-qc"]}
    }

    with patch.dict(app.config, categories_config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        obj.data = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "astro-ph.CO",
                    ],
                    "value": "1705.01122",
                },
            ],
        }
        assert validate(obj.data["arxiv_eprints"], subschema) is None
        set_core_in_extra_data(obj, eng)
        assert "core" not in obj.extra_data


def test_core_is_written_in_extradata_if_article_primary_category_is_core(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {
            "core": ["hep-ph", "math.AP"],
            "non-core": ["astro-ph.CO", "gr-qc"],
        }
    }

    with patch.dict(app.config, categories_config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        obj.data = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "hep-ph",
                        "math.AP",
                    ],
                    "value": "1705.01122",
                },
            ],
        }
        assert validate(obj.data["arxiv_eprints"], subschema) is None
        set_core_in_extra_data(obj, eng)
        assert obj.extra_data["core"]


def test_core_is_not_written_in_extradata_if_article_primary_category_is_not_core(app):
    schema = load_schema("hep")
    subschema = schema["properties"]["arxiv_eprints"]

    categories_config = {
        "ARXIV_CATEGORIES": {"core": ["hep-ph"], "non-core": ["astro-ph.CO", "gr-qc"]}
    }

    with patch.dict(app.config, categories_config):
        data = {}
        extra_data = {}

        obj = MockObj(data, extra_data)
        eng = MockEng()

        obj.data = {
            "arxiv_eprints": [
                {
                    "categories": [
                        "astro-ph.CO",
                        "hep-ph",
                    ],
                    "value": "1705.01122",
                },
            ],
        }
        assert validate(obj.data["arxiv_eprints"], subschema) is None
        set_core_in_extra_data(obj, eng)
        assert "core" not in obj.extra_data


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_pending_in_holding_pen_returns_true_if_something_matched(mock_match):
    mock_match.return_value = iter([{"_id": 1}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data, id=2)
    eng = MockEng()

    assert pending_in_holding_pen(obj, eng)


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_pending_in_holding_pen_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not pending_in_holding_pen(obj, eng)


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched(mock_match):
    schema = load_schema("hep")
    abstracts_schema = schema["properties"]["abstracts"]
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 4328,
        "abstracts": [
            {
                "value": "abstract",
                "source": "arXiv",
            },
        ],
        "titles": [
            {"title": "title"},
        ],
    }

    assert validate(matched_record["abstracts"], abstracts_schema) is None
    assert validate(matched_record["titles"], titles_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 4328,
                        "abstract": "abstract",
                        "title": "title",
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 4328,
                "abstract": "abstract",
                "title": "title",
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_without_abstracts(mock_match):
    schema = load_schema("hep")
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 4328,
        "titles": [
            {
                "title": "title",
            },
        ],
    }

    assert validate(matched_record["titles"], titles_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 4328,
                        "title": "title",
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 4328,
                "title": "title",
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_4_authors(mock_match):
    schema = load_schema("hep")
    authors_schema = schema["properties"]["authors"]
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 4328,
        "titles": [
            {
                "title": "title",
            },
        ],
        "authors": [
            {"full_name": "Author 1"},
            {"full_name": "Author, 2"},
            {"full_name": "Author, 3"},
            {"full_name": "Author, 4"},
        ],
        "authors_count": 4,
    }

    assert validate(matched_record["titles"], titles_schema) is None
    assert validate(matched_record["authors"], authors_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 4328,
                        "title": "title",
                        "authors": [
                            {"full_name": "Author 1"},
                            {"full_name": "Author, 2"},
                            {"full_name": "Author, 3"},
                        ],
                        "authors_count": 4,
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 4328,
                "title": "title",
                "authors": [
                    {"full_name": "Author 1"},
                    {"full_name": "Author, 2"},
                    {"full_name": "Author, 3"},
                ],
                "authors_count": 4,
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_1_author(mock_match):
    schema = load_schema("hep")
    authors_schema = schema["properties"]["authors"]
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 4328,
        "titles": [
            {
                "title": "title",
            },
        ],
        "authors": [
            {"full_name": "Author 1"},
        ],
        "authors_count": 1,
    }

    assert validate(matched_record["titles"], titles_schema) is None
    assert validate(matched_record["authors"], authors_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 4328,
                        "title": "title",
                        "authors": [
                            {"full_name": "Author 1"},
                        ],
                        "authors_count": 1,
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 4328,
                "title": "title",
                "authors": [
                    {"full_name": "Author 1"},
                ],
                "authors_count": 1,
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_number_of_pages(mock_match):
    schema = load_schema("hep")
    titles_schema = schema["properties"]["titles"]
    number_of_pages_schema = schema["properties"]["number_of_pages"]

    matched_record = {
        "control_number": 4328,
        "titles": [
            {
                "title": "title",
            },
        ],
        "number_of_pages": 10,
    }

    assert validate(matched_record["titles"], titles_schema) is None
    assert validate(matched_record["number_of_pages"], number_of_pages_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 4328,
                        "title": "title",
                        "number_of_pages": 10,
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 4328,
                "title": "title",
                "number_of_pages": 10,
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_arxiv_eprints(mock_match):
    schema = load_schema("hep")
    arxiv_eprints_schema = schema["properties"]["arxiv_eprints"]
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 1472986,
        "titles": [
            {
                "title": "title",
            },
        ],
        "arxiv_eprints": [{"categories": ["hep-ph"], "value": "1606.09129"}],
    }

    assert validate(matched_record["titles"], titles_schema) is None
    assert validate(matched_record["arxiv_eprints"], arxiv_eprints_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 1472986,
                        "title": "title",
                        "arxiv_eprint": "1606.09129",
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 1472986,
                "title": "title",
                "arxiv_eprint": "1606.09129",
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_earliest_date(mock_match):
    schema = load_schema("hep")
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 1472986,
        "titles": [
            {
                "title": "title",
            },
        ],
        "earliest_date": "2016-06-29",
    }

    assert validate(matched_record["titles"], titles_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 1472986,
                        "title": "title",
                        "earliest_date": "2016-06-29",
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 1472986,
                "title": "title",
                "earliest_date": "2016-06-29",
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_more_than_1_public_notes(
    mock_match,
):
    schema = load_schema("hep")
    public_notes_schema = schema["properties"]["public_notes"]
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 1472986,
        "titles": [
            {
                "title": "title",
            },
        ],
        "public_notes": [
            {
                "source": "arXiv",
                "value": "4 pages, 4 figures",
            },
            {
                "source": "arXiv",
                "value": "Some other public note",
            },
        ],
    }

    assert validate(matched_record["titles"], titles_schema) is None
    assert validate(matched_record["public_notes"], public_notes_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 1472986,
                        "title": "title",
                        "public_notes": [
                            {"value": "4 pages, 4 figures"},
                            {"value": "Some other public note"},
                        ],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 1472986,
                "title": "title",
                "public_notes": [
                    {"value": "4 pages, 4 figures"},
                    {"value": "Some other public note"},
                ],
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_true_if_something_matched_with_publication_info(
    mock_match,
):
    schema = load_schema("hep")
    publication_info_schema = schema["properties"]["publication_info"]
    titles_schema = schema["properties"]["titles"]

    matched_record = {
        "control_number": 1472986,
        "titles": [
            {
                "title": "title",
            },
        ],
        "publication_info": [
            {
                "artid": "054021",
                "journal_issue": "5",
                "journal_title": "Phys.Rev.D",
                "journal_volume": "94",
                "pubinfo_freetext": "Phys. Rev. D94 (2016) 054021",
                "year": 2016,
            },
        ],
    }

    assert validate(matched_record["titles"], titles_schema) is None
    assert validate(matched_record["publication_info"], publication_info_schema) is None

    mock_match.return_value = iter([{"_source": matched_record}])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={
                "matched_data": [
                    {
                        "control_number": 1472986,
                        "title": "title",
                        "publication_info": [
                            {
                                "artid": "054021",
                                "journal_issue": "5",
                                "journal_title": "Phys.Rev.D",
                                "journal_volume": "94",
                                "pubinfo_freetext": "Phys. Rev. D94 (2016) 054021",
                                "year": 2016,
                            },
                        ],
                    }
                ]
            },
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )
        assert fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = [
            {
                "control_number": 1472986,
                "title": "title",
                "publication_info": [
                    {
                        "artid": "054021",
                        "journal_issue": "5",
                        "journal_title": "Phys.Rev.D",
                        "journal_volume": "94",
                        "pubinfo_freetext": "Phys. Rev. D94 (2016) 054021",
                        "year": 2016,
                    },
                ],
            }
        ]
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_fuzzy_match_returns_false_if_nothing_matched(mock_match):
    mock_match.return_value = iter([])

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()
    with requests_mock.Mocker() as request_mocker:
        request_mocker.register_uri(
            "GET",
            "http://web:8000/matcher/fuzzy-match",
            json={"matched_data": []},
            headers=_get_headers_for_hep_root_table_request(),
            status_code=200,
        )

        assert not fuzzy_match(obj, eng)
        assert "matches" in obj.extra_data

        expected = []
        result = get_value(obj.extra_data, "matches.fuzzy")

        assert expected == result


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_is_fuzzy_match_approved_returns_true_if_there_is_a_match_approved(mock_match):
    data = {}
    extra_data = {"fuzzy_match_approved_id": 4328}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_fuzzy_match_approved(obj, eng)


@patch("inspirehep.modules.workflows.tasks.matching.match")
def test_is_fuzzy_match_approved_returns_False_if_there_is_not_a_match_approved(
    mock_match,
):
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_fuzzy_match_approved(obj, eng)


def test_set_fuzzy_match_approved_in_extradata():
    data = {}
    extra_data = {"fuzzy_match_approved_id": 1}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    set_fuzzy_match_approved_in_extradata(obj, eng)

    expected = 1
    result = get_value(obj.extra_data, "matches.approved")

    assert expected == result


def test_set_fuzzy_match_approved_in_extradata_no_fuzzy_key():
    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    set_fuzzy_match_approved_in_extradata(obj, eng)

    expected = None
    result = get_value(obj.extra_data, "matches.approved")

    assert expected == result
