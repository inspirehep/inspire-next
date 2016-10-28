# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
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

from bat_framework.pages import create_literature


# Components Tests
def test_import_from_arXiv(login):
    """Test the import from arXiv"""
    create_literature.go_to()
    imported_data = create_literature.submit_arxiv_id('hep-th/9711200')

    test_data = {
        'issue': '4',
        'year': '1999',
        'volume': '38',
        'page-range': '1113-1133',
        'author': 'Maldacena, Juan',
        'doi': '10.1023/A:1026654312961',
        'journal': 'International Journal of Theoretical Physics',
        'title': 'The Large N Limit of Superconformal Field Theories and Supergravity',
        'abstract': 'We show that the large $N$ limit of certain conformal field theories'
        }

    assert imported_data == test_data


def test_import_from_doi(login):
    create_literature.go_to()
    imported_data = create_literature.submit_doi_id('10.1086/305772')

    test_data = {
        'issue': '2',
        'year': '1998',
        'volume': '500',
        'page-range': '525-553',
        'author': 'Schlegel, David J.',
        'author-1': 'Finkbeiner, Douglas P.',
        'author-2': 'Davis, Marc',
        'journal': 'The Astrophysical Journal',
        'title': 'Maps of Dust Infrared Emission for Use in Estimation of Reddening and Cosmic Microwave Background Radiation Foregrounds'
        }

    assert imported_data == test_data
