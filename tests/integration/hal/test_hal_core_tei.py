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

import os

import pkg_resources
import pytest
from lxml import etree

from invenio_search.api import current_search_client as es

from inspirehep.modules.hal.core.tei import convert_to_tei
from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.utils.record_getter import get_db_record


@pytest.fixture(scope='function')
def cern_with_hal_id(app):
    """Temporarily add the HAL id to the CERN record."""
    record = get_db_record('ins', 902725)
    record['external_system_identifiers'] = [{'schema': 'HAL', 'value': '300037'}]
    record_insert_or_replace(record)
    es.indices.refresh('records-institutions')

    yield

    record = get_db_record('ins', 902725)
    del record['external_system_identifiers']
    record_insert_or_replace(record)
    es.indices.refresh('records-institutions')


def test_convert_to_tei(cern_with_hal_id):
    record = get_db_record('lit', 1472986)

    schema = etree.XMLSchema(etree.parse(pkg_resources.resource_stream(
        __name__, os.path.join('fixtures', 'aofr.xsd'))))
    result = etree.fromstring(convert_to_tei(record).encode('utf8'))

    assert schema.validate(result)
