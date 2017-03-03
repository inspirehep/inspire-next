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

from flask import current_app
from mock import patch

from inspirehep.modules.records.tasks import update_links


def test_update_links():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'record': {
                '$ref': 'http://localhost:5000/record/1',
            },
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'record': {
                '$ref': 'http://localhost:5000/record/2',
            },
        }


def test_update_links_handles_nested_paths():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'foo.record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {
                    '$ref': 'http://localhost:5000/record/1',
                },
            },
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {
                    '$ref': 'http://localhost:5000/record/2',
                },
            },
        }


def test_update_links_handles_lists():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'foos.record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foos': [
                {'record': {'$ref': 'http://localhost:5000/record/1'}},
                {'record': {'$ref': 'http://localhost:5000/record/2'}},
            ],
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foos': [
                {'record': {'$ref': 'http://localhost:5000/record/2'}},
                {'record': {'$ref': 'http://localhost:5000/record/2'}},
            ],
        }


def test_update_links_ignores_non_whitelisted_paths():
    config = {
        'INSPIRE_REF_UPDATER_WHITELISTS': {
            'literature': [
                'foo.record',
            ],
        },
    }

    with patch.dict(current_app.config, config):
        record = {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {'$ref': 'http://localhost:5000/record/1'},
            },
            'bar': {
                'record': {'$ref': 'http://localhost:5000/record/1'},
            }
        }

        update_links(record, 'http://localhost:5000/record/1', 'http://localhost:5000/record/2')

        assert record == {
            '$schema': 'http://localhost:5000/schemas/record/hep.json',
            'foo': {
                'record': {'$ref': 'http://localhost:5000/record/2'},
            },
            'bar': {
                'record': {'$ref': 'http://localhost:5000/record/1'},
            }
        }
