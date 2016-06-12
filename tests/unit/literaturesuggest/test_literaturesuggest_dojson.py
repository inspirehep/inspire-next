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

from dojson.utils import GroupableOrderedDict

from inspirehep.modules.literaturesuggest.dojson.model import literature


def test_abstracts_from_abstract():
    form = GroupableOrderedDict([
        ('abstract', 'foo bar baz'),
    ])

    expected = [
        {
            'value': 'foo bar baz',
        },
    ]
    result = literature.do(form)

    assert expected == result['abstracts']


def test_abstracts_from_abstract_strips_spaces():
    form = GroupableOrderedDict([
        ('abstract', '    bar    '),
    ])

    expected = [
        {
            'value': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['abstracts']


def test_arxiv_eprints_from_arxiv_id_post_2007():
    form = GroupableOrderedDict([
        ('arxiv_id', '1407.7581v1'),
    ])

    expected = [
        {
            'value': 'arXiv:1407.7581v1',
        },
    ]
    result = literature.do(form)

    assert expected == result['arxiv_eprints']


def test_arxiv_eprints_from_arxiv_id_pre_2007():
    form = GroupableOrderedDict([
        ('arxiv_id', 'math.GT/0309136'),
    ])

    expected = [
        {
            'categories': 'math.GT',
            'value': 'math.GT/0309136',
        },
    ]
    result = literature.do(form)

    assert expected == result['arxiv_eprints']


def test_arxiv_eprints_from_multiple_arxiv_id():
    form = GroupableOrderedDict([
        ('arxiv_id', '1501.00001v1'),
        ('arxiv_id', '0706.0001v2'),
    ])

    expected = [
        {
            'value': 'arXiv:1501.00001v1',
        },
        {
            'value': 'arXiv:0706.0001v2',
        },
    ]
    result = literature.do(form)

    assert expected == result['arxiv_eprints']


def test_dois_from_doi():
    form = GroupableOrderedDict([
        ('doi', 'foo'),
    ])

    expected = [
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['dois']


def test_authors_from_authors_full_name():
    form = {
        'authors': [
            {
                'full_name': 'Foo, Bar',
            },
        ],
    }

    expected = [
        {
            'full_name': 'Foo, Bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['authors']


def test_authors_from_authors_full_name_initials():
    form = {
        'authors': [
            {
                'full_name': 'Foo, B',
            },
        ],
    }

    expected = [
        {
            'full_name': 'Foo, B',
        },
    ]
    result = literature.do(form)

    assert expected == result['authors']


def test_authors_from_authors_full_name_and_affiliation():
    form = {
        'authors': [
            {
                'affiliation': 'Baz',
                'full_name': 'Foo, Bar',
            },
        ],
    }

    expected = [
        {
            'affiliations': [
                {
                    'value': 'Baz',
                },
            ],
            'full_name': 'Foo, Bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['authors']


def test_field_categories_from_categories():
    form = GroupableOrderedDict([
        ('categories', 'foo bar'),
    ])

    expected = [
        {
            'scheme': 'arXiv',
            'term': 'foo',
        },
        {
            'scheme': 'arXiv',
            'term': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['field_categories']


def test_field_categories_from_multiple_categories():
    form = GroupableOrderedDict([
        ('categories', 'foo bar'),
        ('categories', 'baz'),
    ])

    expected = [
        {
            'scheme': 'arXiv',
            'term': 'foo',
        },
        {
            'scheme': 'arXiv',
            'term': 'bar',
        },
        {
            'scheme': 'arXiv',
            'term': 'baz',
        },
    ]
    result = literature.do(form)

    assert expected == result['field_categories']


def test_collaboration_from_collaboration():
    form = {
        'collaboration': 'foo',
    }

    expected = [
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['collaboration']


def test_hidden_notes_from_hidden_note():
    form = {
        'hidden_note': 'foo',
    }

    expected = [
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['hidden_notes']


def test_publication_info_cnum_from_conference_id():
    form = GroupableOrderedDict([
        ('conference_id', 'foo'),
    ])

    expected = [
        {
            'cnum': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_cnum_from_multiple_conference_id():
    form = GroupableOrderedDict([
        ('conference_id', 'foo'),
        ('conference_id', 'bar'),
    ])

    expected = [
        {
            'cnum': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_imprints_date_from_preprint_created():
    form = GroupableOrderedDict([
        ('preprint_created', 'foo'),
    ])

    expected = [
        {
            'date': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['imprints']


def test_imprints_date_from_multiple_preprint_created_updates():
    form = GroupableOrderedDict([
        ('preprint_created', 'foo'),
        ('preprint_created', 'bar'),
    ])

    expected = [
        {
            'date': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['imprints']


def test_thesis_defense_date_and_public_notes_from_defense_date():
    form = GroupableOrderedDict([
        ('defense_date', 'foo'),
    ])

    result = literature.do(form)

    assert result['thesis'] == [
        {
            'defense_date': 'foo',
        }
    ]
    assert result['public_notes'] == [
        {
            'value': 'Presented on foo',
        }
    ]


def test_thesis_defense_date_and_public_notes_from_multiple_defense_date_updates_and_appends():
    form = GroupableOrderedDict([
        ('defense_date', 'foo'),
        ('defense_date', 'bar'),
    ])

    result = literature.do(form)

    assert result['thesis'] == [
        {
            'defense_date': 'bar',
        },
    ]
    assert result['public_notes'] == [
        {
            'value': 'Presented on foo',
        },
        {
            'value': 'Presented on bar',
        },
    ]


def test_thesis_degree_type_from_degree_type():
    form = GroupableOrderedDict([
        ('degree_type', 'foo'),
    ])

    expected = [
        {
            'degree_type': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['thesis']


def test_thesis_degree_type_from_multiple_degree_type_updates():
    form = GroupableOrderedDict([
        ('degree_type', 'foo'),
        ('degree_type', 'bar'),
    ])

    expected = [
        {
            'degree_type': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['thesis']


def test_thesis_university_from_institution():
    form = GroupableOrderedDict([
        ('institution', 'foo'),
    ])

    expected = [
        {
            'university': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['thesis']


def test_thesis_university_from_multiple_institution_updates():
    form = GroupableOrderedDict([
        ('institution', 'foo'),
        ('institution', 'bar'),
    ])

    expected = [
        {
            'university': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['thesis']


def test_thesis_date_from_thesis_date():
    form = GroupableOrderedDict([
        ('thesis_date', 'foo'),
    ])

    expected = [
        {
            'date': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['thesis']


def test_thesis_date_from_multiple_thesis_date_updates():
    form = GroupableOrderedDict([
        ('thesis_date', 'foo'),
        ('thesis_date', 'bar'),
    ])

    expected = [
        {
            'date': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['thesis']


def test_accelerator_experiments_from_experiment():
    form = GroupableOrderedDict([
        ('experiment', 'foo'),
    ])

    expected = [
        {
            'experiment': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['accelerator_experiments']


@pytest.mark.xfail(reason='also populates issue')
def test_publication_info_issue_from_issue():
    form = GroupableOrderedDict([
        ('issue', 'foo'),
    ])

    expected = [
        {
            'journal_issue': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


@pytest.mark.xfail(reason='populates issue instead')
def test_publication_info_issue_from_multiple_issue_updates():
    form = GroupableOrderedDict([
        ('issue', 'foo'),
        ('issue', 'bar'),
    ])

    expected = [
        {
            'journal_issue': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_journal_title_from_journal_title():
    form = GroupableOrderedDict([
        ('journal_title', 'foo'),
    ])

    expected = [
        {
            'journal_title': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_journal_title_from_multiple_journal_title_updates():
    form = GroupableOrderedDict([
        ('journal_title', 'foo'),
        ('journal_title', 'bar'),
    ])

    expected = [
        {
            'journal_title': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_journal_volume_from_volume():
    form = GroupableOrderedDict([
        ('volume', 'foo'),
    ])

    expected = [
        {
            'journal_volume': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_journal_volume_from_multiple_volume_updates():
    form = GroupableOrderedDict([
        ('volume', 'foo'),
        ('volume', 'bar'),
    ])

    expected = [
        {
            'journal_volume': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_year_from_year():
    form = GroupableOrderedDict([
        ('year', 'foo'),
    ])

    expected = [
        {
            'year': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_year_from_multiple_year_updates():
    form = GroupableOrderedDict([
        ('year', 'foo'),
        ('year', 'bar'),
    ])

    expected = [
        {
            'year': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_page_artid_from_page_range_article_id():
    form = GroupableOrderedDict([
        ('page_range_article_id', 'foo'),
    ])

    expected = [
        {
            'page_artid': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_publication_info_page_artid_from_multiple_page_range_article_id_updates():
    form = GroupableOrderedDict([
        ('page_range_article_id', 'foo'),
        ('page_range_article_id', 'bar'),
    ])

    expected = [
        {
            'page_artid': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['publication_info']


def test_languages_from_language_english_or_other():
    form = {
        'language': 'en',
    }

    result = literature.do(form)

    assert 'languages' not in result


def test_languages_from_language_not_english_or_other():
    form = {
        'language': 'ita',
    }

    expected = [
        u'Italian',
    ]
    result = literature.do(form)

    assert expected == result['languages']


def test_license_from_license_url():
    form = GroupableOrderedDict([
        ('license_url', 'foo'),
    ])

    expected = [
        {
            'url': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['license']


def test_license_from_multiple_license_url_appends():
    form = GroupableOrderedDict([
        ('license_url', 'foo'),
        ('license_url', 'bar'),
    ])

    expected = [
        {
            'url': 'foo',
        },
        {
            'url': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['license']


def test_public_notes_from_note():
    form = GroupableOrderedDict([
        ('note', 'foo'),
    ])

    expected = [
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['public_notes']


def test_public_notes_from_multiple_note_prepends():
    form = GroupableOrderedDict([
        ('note', 'foo'),
        ('note', 'bar'),
    ])

    expected = [
        {
            'value': 'bar',
        },
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['public_notes']


def test_report_numbers_from_report_numbers():
    form = {
        'report_numbers': [
            {
                'report_number': 'foo',
            },
        ],
    }

    expected = [
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['report_numbers']


def test_field_categories_from_subject_term():
    form = {
        'subject_term': [
            'foo',
            'bar',
        ]
    }

    expected = [
        {
            'term': 'foo',
            'scheme': 'INSPIRE',
            'source': 'submitter',
        },
        {
            'term': 'bar',
            'scheme': 'INSPIRE',
            'source': 'submitter',
        },
    ]
    result = literature.do(form)

    assert expected == result['field_categories']


def test_thesis_supervisor_from_supervisors():
    form = GroupableOrderedDict([
        ('supervisors', 'foo'),
    ])

    expected = 'foo'
    result = literature.do(form)

    assert expected == result['thesis_supervisor']


def test_titles_from_title():
    form = GroupableOrderedDict([
        ('title', 'foo'),
    ])

    expected = [
        {
            'title': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['titles']


def test_titles_from_multiple_title():
    form = GroupableOrderedDict([
        ('title', 'foo'),
        ('title', 'bar'),
    ])

    expected = [
        {
            'title': 'foo',
        },
        {
            'title': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['titles']


def test_title_translations_from_title_translation():
    form = GroupableOrderedDict([
        ('title_translation', 'foo'),
    ])

    expected = [
        {
            'title': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['title_translations']


def test_urls_and_pdf_from_url():
    form = GroupableOrderedDict([
        ('url', 'foo'),
    ])

    result = literature.do(form)

    assert result['pdf'] == 'foo'
    assert result['urls'] == [
        {
            'value': 'foo',
        },
    ]


def test_urls_and_pdf_from_multiple_url():
    form = GroupableOrderedDict([
        ('url', 'foo'),
        ('url', 'bar'),
    ])

    result = literature.do(form)

    assert result['pdf'] == 'bar'
    assert result['urls'] == [
        {
            'value': 'foo',
        },
        {
            'value': 'bar',
        },
    ]


def test_urls_from_additional_url():
    form = GroupableOrderedDict([
        ('additional_url', 'foo'),
    ])

    expected = [
        {
            'value': 'foo',
        },
    ]
    result = literature.do(form)

    assert expected == result['urls']


def test_urls_from_multiple_additional_url():
    form = GroupableOrderedDict([
        ('additional_url', 'foo'),
        ('additional_url', 'bar'),
    ])

    expected = [
        {
            'value': 'foo',
        },
        {
            'value': 'bar',
        },
    ]
    result = literature.do(form)

    assert expected == result['urls']
