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

from jsonref import JsonRef

from inspirehep.modules.records.json_ref_loader import (
    AbstractRecordLoader, DatabaseJsonLoader, ESJsonLoader, replace_refs)
from inspirehep.utils.record_getter import RecordGetterError


def _build_url(endpoint='literature', recid='42'):
    server = current_app.config['SERVER_NAME']
    if not server.startswith('http://'):
        server = 'http://{}'.format(server)
    return '{}/api/{}/{}'.format(server, endpoint, recid)


@patch('inspirehep.modules.records.json_ref_loader.record_getter.get_es_record')
@patch('inspirehep.modules.records.json_ref_loader.record_getter.get_db_record')
def test_replace_refs_correct_sources(get_db_rec, get_es_rec):
    with_es_record = {'ES': 'ES'}
    with_db_record = {'DB': 'DB'}

    get_es_rec.return_value = with_es_record
    get_db_rec.return_value = with_db_record

    db_rec = replace_refs({'$ref': _build_url()}, 'db')
    es_rec = replace_refs({'$ref': _build_url()}, 'es')

    assert db_rec == with_db_record
    assert es_rec == with_es_record


@patch('inspirehep.modules.records.json_ref_loader.get_pid_type_from_endpoint')
@patch('inspirehep.modules.records.json_ref_loader.JsonLoader.get_remote_json')
@patch('inspirehep.modules.records.json_ref_loader.AbstractRecordLoader.get_record')
def test_abstract_loader_url_fallbacks(get_record, super_get_r_j, g_p_t_f_e):
    with_super = {'SUPER': 'SUPER'}
    with_actual = {'ACTUAL': 'ACTUAL'}
    g_p_t_f_e.return_value = 'pt'
    super_get_r_j.return_value = with_super
    get_record.return_value = with_actual

    # Check against prod SERVER_NAME
    config = {'SERVER_NAME': 'http://inspirehep.net'}

    with patch.dict(current_app.config, config):
        expect_actual = JsonRef({'$ref': 'http://inspirehep.net/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        expect_actual = JsonRef({'$ref': '/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        expect_super = JsonRef({'$ref': 'http://otherhost.net/api/e/1'},
                               loader=AbstractRecordLoader())
        assert expect_super == with_super

    # Check against dev SERVER_NAME
    config = {'SERVER_NAME': 'localhost:5000'}

    with patch.dict(current_app.config, config):
        expect_actual = JsonRef({'$ref': 'http://localhost:5000/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        expect_actual = JsonRef({'$ref': '/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        expect_super = JsonRef({'$ref': 'http://inspirehep.net/api/e/1'},
                               loader=AbstractRecordLoader())
        assert expect_super == with_super

    # Check against prod https SERVER_NAME
    config = {'SERVER_NAME': 'https://inspirehep.net'}

    with patch.dict(current_app.config, config):
        expect_actual = JsonRef({'$ref': 'https://inspirehep.net/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        expect_actual = JsonRef({'$ref': '/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        # https should be backwards compatible with resources indexed with http://.
        expect_actual = JsonRef({'$ref': 'http://inspirehep.net/api/e/1'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual

        expect_super = JsonRef({'$ref': 'http://otherhost.net/api/e/1'},
                               loader=AbstractRecordLoader())
        assert expect_super == with_super


@patch('inspirehep.modules.records.json_ref_loader.get_pid_type_from_endpoint')
@patch('inspirehep.modules.records.json_ref_loader.AbstractRecordLoader.get_record')
def test_abstract_loader_recid_parsing(get_record, g_p_t_f_e):
    with_actual = {'ACTUAL': 'ACTUAL'}
    g_p_t_f_e.side_effect = ['pt1', 'pt2', 'pt3']
    get_record.return_value = with_actual

    config = {'SERVER_NAME': 'http://inspirehep.net'}

    with patch.dict(current_app.config, config):
        expect_actual = JsonRef({'$ref': 'http://inspirehep.net/api/e1/1'},
                                loader=AbstractRecordLoader())
        # Force evaluation of get_record by this assertion.
        assert expect_actual == with_actual
        get_record.assert_called_with('pt1', '1')

        expect_actual = JsonRef({'$ref': '/api/e2/2'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual
        get_record.assert_called_with('pt2', '2')

        expect_actual = JsonRef({'$ref': '/e3/3/'},
                                loader=AbstractRecordLoader())
        assert expect_actual == with_actual
        get_record.assert_called_with('pt3', '3')


@patch('inspirehep.modules.records.json_ref_loader.AbstractRecordLoader.get_record')
def test_abstract_loader_return_none(get_record):
    config = {'SERVER_NAME': 'http://inspirehep.net'}

    with patch.dict(current_app.config, config):
        expect_none = JsonRef({'$ref': 'http://inspirehep.net'},
                              loader=AbstractRecordLoader())
        assert expect_none == None  # noqa: E711
        expect_none = JsonRef({'$ref': 'http://inspirehep.net/'},
                              loader=AbstractRecordLoader())
        assert expect_none == None  # noqa: E711
        expect_none = JsonRef({'$ref': 'http://inspirehep.net/bad'},
                              loader=AbstractRecordLoader())
        assert expect_none == None  # noqa: E711
        assert get_record.call_count == 0


@patch('inspirehep.modules.records.json_ref_loader.get_pid_type_from_endpoint')
@patch('inspirehep.modules.records.json_ref_loader.record_getter.get_es_record')
@patch('inspirehep.modules.records.json_ref_loader.record_getter.get_db_record')
def test_specific_loaders_return_none(get_db_rec, get_es_rec, g_p_t_f_e):
    g_p_t_f_e.return_value = 'pt'
    get_es_rec.side_effect = RecordGetterError('err', None)
    get_db_rec.side_effect = RecordGetterError('err', None)

    config = {'SERVER_NAME': 'http://inspirehep.net'}

    with patch.dict(current_app.config, config):
        expect_none = JsonRef({'$ref': 'http://inspirehep.net/api/e/1'},
                              loader=DatabaseJsonLoader())
        assert expect_none == None  # noqa: E711
        expect_none = JsonRef({'$ref': 'http://inspirehep.net/api/e/2'},
                              loader=ESJsonLoader())
        assert expect_none == None  # noqa: E711
        assert get_db_rec.call_count == 1
        assert get_es_rec.call_count == 1
