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

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.disambiguation.logic import _create_distance_signature


def test_create_distance_signature_method(small_app):
    """Test the method responsible for creating data in Beard format."""
    pid = PersistentIdentifier.get("literature", 4328)
    publication_id = str(pid.object_uuid)

    signatures_map = {
        'aabe5373-39bf-4d27-bb91-2aec593940a9': {
            'author_affiliation': 'Copenhagen U.',
            'author_claimed': False,
            'author_name': 'Glashow, S.L.',
            'author_recid': False,
            'publication_id': publication_id,
            'signature_id': 'aabe5373-39bf-4d27-bb91-2aec593940a9'
        }
    }

    uuid = 'aabe5373-39bf-4d27-bb91-2aec593940a9'

    distance_signature = {
        'author_affiliation': 'Copenhagen U.',
        'author_claimed': False,
        'author_name': 'Glashow, S.L.',
        'author_recid': False,
        'publication_id': publication_id,
        'signature_id': 'aabe5373-39bf-4d27-bb91-2aec593940a9',
        'publication': {
            'publication_id': publication_id,
            'year': '1961',
            'authors': ['Glashow, S.L.']
        }
    }

    assert _create_distance_signature(signatures_map, uuid) == \
        distance_signature
