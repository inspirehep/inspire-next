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

from six import binary_type
from mock import patch

from inspirehep.modules.workflows.tasks.classifier import classify_paper
from mocks import MockEng, MockObj


@patch('inspirehep.modules.workflows.tasks.classifier.get_pdf_in_workflow')
def test_classify_paper_with_fulltext(get_pdf_in_workflow, tmpdir):
    obj = MockObj({}, {})
    eng = MockEng()
    fulltext = tmpdir.join('fulltext.txt')
    fulltext.write('Higgs boson')
    get_pdf_in_workflow.return_value = binary_type(fulltext)

    expected = [
        {
            'number': 1,
            'keyword': 'Higgs particle'
        }
    ]

    classify_paper(
        taxonomy="HEPont.rdf",
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
    )(obj, eng)

    assert obj.extra_data['classifier_results']['complete_output']['core_keywords'] == expected
    assert obj.extra_data['classifier_results']['fulltext_used'] is True


@patch('inspirehep.modules.workflows.tasks.classifier.get_pdf_in_workflow')
def test_classify_paper_with_no_fulltext(get_pdf_in_workflow):
    data = {
        'titles': [
            {
                'title': 'Some title',
            },
        ],
        'abstracts': [
            {
                'value': 'Very interesting paper about the Higgs boson.'
            },
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    get_pdf_in_workflow.return_value = None

    expected = [
        {
            'number': 1,
            'keyword': 'Higgs particle'
        }
    ]

    classify_paper(
        taxonomy="HEPont.rdf",
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
    )(obj, eng)

    assert obj.extra_data['classifier_results']['complete_output']['core_keywords'] == expected
    assert obj.extra_data['classifier_results']['fulltext_used'] is False


@patch('inspirehep.modules.workflows.tasks.classifier.get_pdf_in_workflow')
def test_classify_paper_uses_keywords(get_pdf_in_workflow):
    data = {
        'titles': [
            {
                'title': 'Some title',
            },
        ],
        'keywords': [
            {
                'value': 'Higgs boson',
            },
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()
    get_pdf_in_workflow.return_value = None

    expected = [
        {
            'number': 1,
            'keyword': 'Higgs particle'
        }
    ]

    classify_paper(
        taxonomy="HEPont.rdf",
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
    )(obj, eng)

    assert obj.extra_data['classifier_results']['complete_output']['core_keywords'] == expected
    assert obj.extra_data['classifier_results']['fulltext_used'] is False
