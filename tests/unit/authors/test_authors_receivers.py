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

import httpretty
import mock
import pytest
from flask import current_app

from inspire_dojson.utils import validate
from inspire_schemas.utils import load_schema
from inspirehep.modules.authors import receivers


def test_name_variations():
    json_dict = {
        "authors": [{
            "full_name": "John Richard Ellis"
        }]
    }

    receivers.generate_name_variations(None, json_dict)

    assert(
        json_dict['authors'][0]['name_variations'] == [
            'Ellis',
            'Ellis J',
            'Ellis J R',
            'Ellis J Richard',
            'Ellis John',
            'Ellis John R',
            'Ellis John Richard',
            'Ellis R',
            'Ellis Richard',
            'Ellis, J',
            'Ellis, J R',
            'Ellis, J Richard',
            'Ellis, John',
            'Ellis, John R',
            'Ellis, John Richard',
            'Ellis, R',
            'Ellis, Richard',
            'J Ellis',
            'J R Ellis',
            'J Richard Ellis',
            'John Ellis',
            'John R Ellis',
            'John Richard Ellis',
            'R Ellis',
            'Richard Ellis'])


@pytest.mark.httpretty
def test_phonetic_block_generation_ascii():
    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
    }

    with mock.patch.dict(current_app.config, extra_config):
        httpretty.register_uri(
            httpretty.POST,
            "{base_url}/text/phonetic_blocks".format(
                base_url=current_app.config.get('BEARD_API_URL')),
            content_type="application/json",
            body='{"phonetic_blocks": {"John Richard Ellis": "ELj"}}',
            status=200)

        json_dict = {
            "authors": [{
                "full_name": "John Richard Ellis"
            }]
        }

        receivers.assign_phonetic_block(json_dict)

        assert json_dict['authors'][0]['signature_block'] == "ELj"


@pytest.mark.httpretty
def test_phonetic_block_generation_broken():
    schema = load_schema('hep')
    subschema = schema['properties']['authors']

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
    }

    with mock.patch.dict(current_app.config, extra_config):
        httpretty.register_uri(
            httpretty.POST,
            "{base_url}/text/phonetic_blocks".format(
                base_url=current_app.config.get('BEARD_API_URL')),
            content_type="application/json",
            body='{"phonetic_blocks": {}}',
            status=200)

        json_dict = {
            "authors": [{
                "full_name": "** NOT VALID **"
            }]
        }

        receivers.assign_phonetic_block(json_dict)

        assert validate(json_dict['authors'], subschema) is None
        assert json_dict['authors'][0].get('signature_block') is None


@pytest.mark.httpretty
def test_phonetic_block_generation_unicode():
    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
    }

    with mock.patch.dict(current_app.config, extra_config):
        httpretty.register_uri(
            httpretty.POST,
            "{base_url}/text/phonetic_blocks".format(
                base_url=current_app.config.get('BEARD_API_URL')),
            content_type="application/json",
            body=u'{"phonetic_blocks": {"Grzegorz Jacenków": "JACANCg"}}',
            status=200)

        json_dict = {
            "authors": [{
                "full_name": u"Grzegorz Jacenków"
            }]
        }

        receivers.assign_phonetic_block(json_dict)

        assert json_dict['authors'][0]['signature_block'] == "JACANCg"


def test_uuid_generation():
    json_dict = {
        "authors": [{
            "full_name": "John Doe",
            "uuid": "I am unique"
        }, {
            "full_name": "John Richard Ellis"
        }]
    }

    receivers.assign_uuid(json_dict)

    # Check if the author with existing UUID has still the same UUID.
    assert(json_dict['authors'][0]['uuid'] == "I am unique")

    # Check if the author with no UUID got one.
    assert(json_dict['authors'][1]['uuid'] is not None)
