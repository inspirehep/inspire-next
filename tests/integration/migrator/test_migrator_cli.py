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

import json
import os

import pkg_resources
import pytest
from flask import current_app

from mock import patch
from invenio_db import db
from inspirehep.modules.migrator.cli import migrate
from inspirehep.modules.migrator.models import LegacyRecordsMirror
from inspirehep.modules.migrator.tasks import populate_mirror_from_file


def test_migrate_file_halts_in_debug_mode(app_cli_runner):
    config = {
        'DEBUG': True
    }
    with patch.dict(current_app.config, config):
        file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663923.xml'))

        result = app_cli_runner.invoke(migrate, ['file', file_name])

        assert result.exit_code == 1
        assert 'DEBUG' in result.output


def test_migrate_file_doesnt_halt_in_debug_mode_when_forced(app_cli_runner):
    config = {
        'DEBUG': True
    }
    with patch.dict(current_app.config, config):
        file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663923.xml'))

        result = app_cli_runner.invoke(migrate, ['file', '-f', file_name])

        assert result.exit_code == 0
        assert 'DEBUG' not in result.output


def test_migrate_file(app_cli_runner, api_client):
    file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663923.xml'))

    result = app_cli_runner.invoke(migrate, ['file', '-w', '-f', file_name])
    response = api_client.get('/literature/1663923')

    assert result.exit_code == 0
    assert response.status_code == 200
    assert json.loads(response.data)['metadata']['control_number'] == 1663923


def test_migrate_file_mirror_only(app_cli_runner, api_client):
    file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml'))

    result = app_cli_runner.invoke(migrate, ['file', '-w', '-m', '-f', file_name])
    prod_record = LegacyRecordsMirror.query.get(1663924)
    response = api_client.get('/literature/1663924')

    assert result.exit_code == 0
    assert prod_record.recid == 1663924
    assert response.status_code == 404


def test_migrate_mirror_halts_in_debug_mode(app_cli_runner):
    config = {
        'DEBUG': True
    }
    with patch.dict(current_app.config, config):
        result = app_cli_runner.invoke(migrate, ['mirror', '-a'])

        assert result.exit_code == 1
        assert 'DEBUG' in result.output


def test_migrate_mirror_doesnt_halt_in_debug_mode_when_forced(app_cli_runner):
    config = {
        'DEBUG': True
    }
    with patch.dict(current_app.config, config):
        result = app_cli_runner.invoke(migrate, ['mirror', '-f'])

        assert result.exit_code == 0
        assert 'DEBUG' not in result.output


def test_migrate_mirror_migrates_pending(app_cli_runner, api_client):
    file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml'))
    populate_mirror_from_file(file_name)

    result = app_cli_runner.invoke(migrate, ['mirror', '-w', '-f'])
    response = api_client.get('/literature/1663924')

    assert result.exit_code == 0
    assert response.status_code == 200
    assert json.loads(response.data)['metadata']['control_number'] == 1663924


def test_migrate_mirror_broken_migrates_invalid(app_cli_runner, api_client):
    file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663927_broken.xml'))
    populate_mirror_from_file(file_name)

    result = app_cli_runner.invoke(migrate, ['mirror', '-w', '-f'])
    response = api_client.get('/literature/1663927')

    assert result.exit_code == 0
    assert response.status_code == 404  # it's broken

    prod_record = LegacyRecordsMirror.query.get(1663927)
    prod_record.marcxml = prod_record.marcxml.replace('Not a date', '2018')

    assert prod_record.valid is False

    db.session.merge(prod_record)

    result = app_cli_runner.invoke(migrate, ['mirror', '-w', '-f', '-b'])
    response = api_client.get('/literature/1663927')

    assert result.exit_code == 0
    assert response.status_code == 200
    assert json.loads(response.data)['metadata']['control_number'] == 1663927


@pytest.mark.xfail(
    reason='''Running this test in the full suite fails because other tests
    modify 2 records in the DB, but this test remigrates their original
    version, which fails ES indexing because of the version bug with the
    citation counts.'''
)
def test_migrate_mirror_all_migrates_all(app_cli_runner, api_client):
    file_name = pkg_resources.resource_filename(__name__, os.path.join('fixtures', '1663924.xml'))
    populate_mirror_from_file(file_name)

    result = app_cli_runner.invoke(migrate, ['mirror', '-w', '-f'])
    response = api_client.get('/literature/1663924')

    assert result.exit_code == 0
    assert response.status_code == 200

    prod_record = LegacyRecordsMirror.query.get(1663924)
    prod_record.marcxml = prod_record.marcxml.replace('A Status report on', 'A funny joke about')

    assert prod_record.valid is True

    db.session.merge(prod_record)

    result = app_cli_runner.invoke(migrate, ['mirror', '-w', '-f', '-a'])
    response = api_client.get('/literature/1663924')

    assert result.exit_code == 0
    assert response.status_code == 200
    assert 'A funny joke' in json.loads(response.data)['metadata']['abstracts'][0]['value']
