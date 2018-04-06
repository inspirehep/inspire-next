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

"""Workflows configuration."""

from __future__ import absolute_import, division, print_function


#
# Configuration used when matching references.
#

WORKFLOWS_REFERENCE_MATCHER_DEFAULT_CONFIG = {
    'algorithm': [
        {
            'queries': [
                {
                    'path': 'reference.arxiv_eprint',
                    'search_path': 'arxiv_eprints.value.raw',
                    'type': 'exact',
                },
                {
                    'path': 'reference.dois',
                    'search_path': 'dois.value.raw',
                    'type': 'exact',
                },
                {
                    'path': 'reference.isbn',
                    'search_path': 'isbns.value.raw',
                    'type': 'exact',
                },
                {
                    'path': 'reference.report_numbers',
                    'search_path': 'report_numbers.value.fuzzy',
                    'type': 'exact',
                },
                {
                    'paths': [
                        'reference.publication_info.journal_title',
                        'reference.publication_info.journal_volume',
                        'reference.publication_info.artid',
                    ],
                    'search_paths': [
                        'publication_info.journal_title.raw',
                        'publication_info.journal_volume',
                        'publication_info.artid',
                    ],
                    'type': 'nested',
                },
                {
                    'paths': [
                        'reference.publication_info.journal_title',
                        'reference.publication_info.journal_volume',
                        'reference.publication_info.page_start',
                    ],
                    'search_paths': [
                        'publication_info.journal_title.raw',
                        'publication_info.journal_volume',
                        'publication_info.page_start',
                    ],
                    'type': 'nested',
                },
            ],
        },
    ],
    'doc_type': 'hep',
    'index': 'records-hep',
    'source': [
        'control_number',
    ],
}
"""TODO."""

WORKFLOWS_REFERENCE_MATCHER_JHEP_AND_JCAP_CONFIG = {
    'algorithm': [
        {
            'queries': [
                {
                    'path': 'reference.arxiv_eprint',
                    'search_path': 'arxiv_eprints.value.raw',
                    'type': 'exact',
                },
                {
                    'path': 'reference.dois',
                    'search_path': 'dois.value.raw',
                    'type': 'exact',
                },
                {
                    'path': 'reference.isbn',
                    'search_path': 'isbns.value.raw',
                    'type': 'exact',
                },
                {
                    'path': 'reference.report_numbers',
                    'search_path': 'report_numbers.value.fuzzy',
                    'type': 'exact',
                },
                {
                    'paths': [
                        'reference.publication_info.journal_title',
                        'reference.publication_info.journal_volume',
                        'reference.publication_info.year',
                        'reference.publication_info.artid',
                    ],
                    'search_paths': [
                        'publication_info.journal_title.raw',
                        'publication_info.journal_volume',
                        'publication_info.year',
                        'publication_info.artid',
                    ],
                    'type': 'nested',
                },
                {
                    'paths': [
                        'reference.publication_info.journal_title',
                        'reference.publication_info.journal_volume',
                        'reference.publication_info.year',
                        'reference.publication_info.page_start',
                    ],
                    'search_paths': [
                        'publication_info.journal_title.raw',
                        'publication_info.journal_volume',
                        'publication_info.year',
                        'publication_info.page_start',
                    ],
                    'type': 'nested',
                },
            ],
        },
    ],
    'doc_type': 'hep',
    'index': 'records-hep',
    'source': [
        'control_number',
    ],
}
"""TODO."""

WORKFLOWS_REFERENCE_MATCHER_DATA_CONFIG = {
    'algorithm': [
        {
            'queries': [
                {
                    'path': 'reference.dois',
                    'search_path': 'dois.value.raw',
                    'type': 'exact',
                },
            ],
        },
    ],
    'doc_type': 'data',
    'index': 'records-data',
    'source': [
        'control_number',
    ],
}
"""TODO."""
