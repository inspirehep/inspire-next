# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.disambiguation.records import (
    _get_author_schema,
    create_author,
)
from inspirehep.modules.records.api import InspireRecord


def test_get_author_schema_method(small_app):
    """Test the method responsible for generating author schema URL."""
    author_schema_result = "http://localhost:5000/schemas/records/authors.json"

    assert _get_author_schema() == author_schema_result


def test_create_author_method(small_app):
    """Test the method for generating new author profiles."""
    signature = {
        'affiliations': [{'value': 'Copenhagen U.'}],
        'curated_relation': False,
        'full_name': 'Glashow, S.L.',
        'uuid': '6a3d43be-e962-4c20-8908-a81bd39447b5'
    }

    recid = create_author(signature)
    pid = PersistentIdentifier.get('aut', recid)
    record = InspireRecord.get_record(pid.object_uuid)

    assert record['_collections'] == ['Authors']
    assert record['name'] == {'value': 'Glashow, S.L.'}
    assert record['positions'] == [{'institution': {'name': 'Copenhagen U.'}}]


@pytest.mark.xfail
def test_update_authors_recid_method(small_app):
    """Test the method responsible for updating author's recid."""
    from inspirehep.modules.disambiguation.tasks import update_authors_recid

    pid = PersistentIdentifier.get('lit', 4328)
    publication_id = str(pid.object_uuid)

    signature = InspireRecord.get_record(publication_id)['authors'][0]['uuid']
    profile_recid = '314159265'

    update_authors_recid(publication_id, signature, profile_recid)

    assert InspireRecord.get_record(publication_id)['authors'][0]['recid'] == \
        profile_recid
