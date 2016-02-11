# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for the matching."""

from flask import current_app

import httpretty

from invenio_base.wrappers import lazy_import

from invenio_testing import InvenioTestCase

import mock

import pytest


Record = lazy_import('invenio_records.api.Record')


class MatchingTests(InvenioTestCase):

    """Tests for the matching."""

    def setup_class(self):
        """Sets up Mock object."""
        class MockObj(object):
            def __init__(self):
                self._extra_data = {'record_matches': {}}

            @property
            def extra_data(self):
                return self._extra_data

            @property
            def model(self):
                return 'banana'

        class MockWorkflowDefinition(object):
            def model(self, obj):
                return obj.model

        class MockEng(object):
            @property
            def workflow_definition(self):
                return MockWorkflowDefinition()

        self.MockObj = MockObj
        self.MockEng = MockEng

    @httpretty.activate
    def test_search_with_result(self):
        """Good search results are handled correctly."""
        from inspirehep.modules.workflows.tasks.matching import search

        httpretty.register_uri(
            httpretty.GET,
            current_app.config['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
            body='[1234]',
            content_type='application/json'
        )

        result = search('035:"oai:arXiv.org:1505.12345"')

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0] == 1234)

    @httpretty.activate
    def test_search_without_result(self):
        """Empty search results are handled correctly."""
        from inspirehep.modules.workflows.tasks.matching import search

        httpretty.register_uri(
            httpretty.GET,
            current_app.config['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
            body='[]',
            content_type='application/json'
        )

        result = search('035:"oai:arXiv.org:1505.12345"')

        self.assertEqual(len(result), 0)

    @httpretty.activate
    def test_search_with_bad_result(self):
        """Bad search results raise an exception."""
        from inspirehep.modules.workflows.tasks.matching import search

        httpretty.register_uri(
            httpretty.GET,
            current_app.config['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
            body='<html></html>',
        )

        with pytest.raises(ValueError):
            search('035:"oai:arXiv.org:1505.12345"')

    @mock.patch('inspirehep.modules.workflows.tasks.matching.search', return_value=[1234])
    def test_match_by_arxiv_id_with_result(self, search):
        """Good match_by_arxiv_id results are handled correctly."""
        from inspirehep.modules.workflows.tasks.matching import match_by_arxiv_id

        record = Record({'arxiv_id': 'arXiv:1505.12345'})

        result = match_by_arxiv_id(record)

        self.assertTrue(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_arxiv_id_from_record', return_value=[])
    def test_match_by_arxiv_id_without_result(self, mock_get_arxiv_id_from_record):
        """Empty match_by_arxiv_id_results are handled correctly."""
        from inspirehep.modules.workflows.tasks.matching import match_by_arxiv_id

        record = Record({})

        result = match_by_arxiv_id(record)

        self.assertEqual(result, [])

    @mock.patch('inspirehep.modules.workflows.tasks.matching.search', return_value=[1234])
    def test_match_by_arxiv_eprints_with_result(self, search):
        """Can also match on the arxiv_eprints.value key."""
        from inspirehep.modules.workflows.tasks.matching import match_by_arxiv_id

        record = Record({
            'arxiv_eprints': [
                {
                    'value': 'arXiv:1505.12345',
                    'source': 'arXiv',
                }
            ]
        })

        result = match_by_arxiv_id(record)

        self.assertTrue(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.search', return_value=[1234])
    def test_match_by_doi_with_result(self, search):
        """Good match_by_doi results are handled correctly."""
        from inspirehep.modules.workflows.tasks.matching import match_by_doi

        record = Record({"dois": {"value": "10.1086/305772"}})

        result = match_by_doi(record)

        self.assertTrue(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_record_from_model')
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_arxiv_id', return_value=[1])
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_doi', return_value=[2])
    def test_match_task_both_with_result(self, match_by_doi, match_by_arxiv_id, get_record_from_model):
        """Check result for match with both arXiv and DOI."""
        from inspirehep.modules.workflows.tasks.matching import match

        obj = self.MockObj()
        eng = self.MockEng()

        record = Record({'titles': [{'title': 'foo'}]})
        get_record_from_model.return_value = record

        result = match(obj, eng)

        self.assertTrue(result)
        self.assertTrue(len(obj.extra_data['record_matches']['recids']) == 2)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_record_from_model')
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_arxiv_id', return_value=[1])
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_doi', return_value=[])
    def test_match_task_with_arxiv_id_result(self, match_by_doi, match_by_arxiv_id, get_record_from_model):
        """Check result for match with arXiv."""
        from inspirehep.modules.workflows.tasks.matching import match

        obj = self.MockObj()
        eng = self.MockEng()

        record = Record({'titles': [{'title': 'foo'}]})
        get_record_from_model.return_value = record

        result = match(obj, eng)

        self.assertTrue(result)
        self.assertEqual(["1"], obj.extra_data['record_matches']['recids'])

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_record_from_model')
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_arxiv_id', return_value=[])
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_doi', return_value=[2])
    def test_match_task_second_with_doi_result(self, match_by_doi, match_by_arxiv_id, get_record_from_model):
        """Check result for match with DOI."""
        from inspirehep.modules.workflows.tasks.matching import match

        obj = self.MockObj()
        eng = self.MockEng()

        record = Record({'titles': [{'title': 'foo'}]})
        get_record_from_model.return_value = record

        result = match(obj, eng)

        self.assertTrue(result)
        self.assertEqual(["2"], obj.extra_data['record_matches']['recids'])

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_record_from_model')
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_arxiv_id', return_value=[])
    @mock.patch('inspirehep.modules.workflows.tasks.matching.match_by_doi', return_value=[])
    def test_match_task_without_result(self, match_by_doi, match_by_arxiv_id, get_record_from_model):
        """Check result for no matches."""
        from inspirehep.modules.workflows.tasks.matching import match

        obj = self.MockObj()
        eng = self.MockEng()

        record = Record({'titles': [{'title': 'foo'}]})
        get_record_from_model.return_value = record

        result = match(obj, eng)

        self.assertFalse(result)
        self.assertEqual([], obj.extra_data['record_matches']['recids'])

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_record_from_model')
    @mock.patch('inspirehep.modules.workflows.tasks.matching._match')
    def test_match_with_invenio_matcher_task_with_result(self, _match, get_record_from_model):
        """Check invenio-matcher multiple results."""
        from invenio_matcher.models import MatchResult
        from inspirehep.modules.workflows.tasks.matching import match_with_invenio_matcher

        obj = self.MockObj()
        eng = self.MockEng()

        _match.return_value.__iter__.return_value = iter([
            MatchResult(1, Record({"control_number": "1"}), 1.0),
            MatchResult(2, Record({"control_number": "2"}), 1.0),
        ])

        record = Record({'titles': [{'title': 'foo'}]})
        get_record_from_model.return_value = record

        result = match_with_invenio_matcher()(obj, eng)

        self.assertTrue(result)
        self.assertTrue(len(obj.extra_data['record_matches']['recids']) == 2)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.get_record_from_model')
    @mock.patch('inspirehep.modules.workflows.tasks.matching._match')
    def test_match_with_invenio_matcher_task_without_result(self, _match, get_record_from_model):
        """Check invenio-matcher without results."""
        from inspirehep.modules.workflows.tasks.matching import match_with_invenio_matcher

        obj = self.MockObj()
        eng = self.MockEng()

        _match.return_value.__iter__.return_value = iter([])

        record = Record({'titles': [{'title': 'foo'}]})
        get_record_from_model.return_value = record

        result = match_with_invenio_matcher()(obj, eng)

        self.assertFalse(result)
        self.assertEqual([], obj.extra_data['record_matches']['recids'])

    @mock.patch('inspirehep.modules.workflows.tasks.matching.cfg', {'INSPIRE_ACCEPTED_CATEGORIES': ['foo']})
    def test_was_already_harvested_true(self):
        """Check already harvested check with match."""
        from inspirehep.modules.workflows.tasks.matching import was_already_harvested

        record = Record({'subject_terms': [{'term': 'FOO'}]})

        result = was_already_harvested(record)

        self.assertTrue(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.cfg', {'INSPIRE_ACCEPTED_CATEGORIES': ['foo']})
    def test_was_already_harvested_false(self):
        """Check already harvested check without match."""
        from inspirehep.modules.workflows.tasks.matching import was_already_harvested

        record = Record({'subject_terms': [{'term': 'bar'}]})

        result = was_already_harvested(record)

        self.assertIsNone(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.date_older_than', return_value=True)
    def test_is_too_old_earliest_date_true(self, date_older_than):
        """Check record is too old to harvest (earliest_date)."""
        from inspirehep.modules.workflows.tasks.matching import is_too_old

        record = Record({'earliest_date': '1993-02-02'})

        result = is_too_old(record)

        self.assertTrue(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.date_older_than', return_value=True)
    def test_is_too_old_preprint_date_true(self, date_older_than):
        """Check record is too old to harvest (preprint_date)."""
        from inspirehep.modules.workflows.tasks.matching import is_too_old

        record = Record({'preprint_date': '1993-02-02'})

        result = is_too_old(record)

        self.assertTrue(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.date_older_than', return_value=False)
    def test_is_too_old_false(self, date_older_than):
        """Check record is not too old to harvest."""
        from inspirehep.modules.workflows.tasks.matching import is_too_old

        record = Record({'earliest_date': '1993-02-02'})

        result = is_too_old(record)

        self.assertIsNone(result)

    @mock.patch('inspirehep.modules.workflows.tasks.matching.BibWorkflowObject')
    def test_update_old_object_success(self, BWO):
        """Check update of old record."""
        from inspirehep.modules.workflows.tasks.matching import update_old_object

        class MockBWO(object):
            def __init__(self, data):
                self._data = data

            @property
            def data(self):
                return self._data

            @property
            def extra_data(self):
                return {'holdingpen_ids': [1]}

            def set_data(self, data):
                self._data = data

            def save(self):
                pass

        obj = MockBWO('foo')
        old_obj = MockBWO('bar')

        BWO.query.get = mock.Mock(return_value=old_obj)

        update_old_object(obj)

        self.assertEqual(old_obj._data, 'foo')

    def test_update_old_object_failure(self):
        """Check record is not updated."""
        from inspirehep.modules.workflows.tasks.matching import update_old_object

        class MockLog(object):
            def error(self, msg):
                self.msg = msg

        class MockBWO(object):
            @property
            def extra_data(self):
                return {'holdingpen_ids': []}

            @property
            def log(self):
                return MockLog()

        obj = MockBWO()
        self.assertRaises(Exception, update_old_object, obj)
