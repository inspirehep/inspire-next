# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Unit tests for the invenio_knowledge adapters."""

from collections import namedtuple

from invenio_testing import InvenioTestCase

import mock


class KnowledgeTests(InvenioTestCase):

    """Unit tests for the invenio_knowledge adapters."""

    @mock.patch('inspirehep.utils.knowledge.kb_mapping_exists')
    def test_get_value_no_mapping(self, kb_m_e):
        kb_m_e.return_value = False

        from inspirehep.utils.knowledge import get_value

        self.assertIsNone(get_value('kb', ['foo', 'bar']))


    @mock.patch('inspirehep.utils.knowledge.kb_mapping_exists')
    @mock.patch('inspirehep.utils.knowledge.get_kb_mappings')
    def test_get_value_in_one_mapping(self, get_kb_m, kb_m_e):
        get_kb_m.side_effect = [[{'value': 'baz'}]]
        kb_m_e.side_effect = [False, True]

        from inspirehep.utils.knowledge import get_value

        expected = 'baz'
        result = get_value('kb', ['foo', 'bar'])

        self.assertEqual(expected, result)

    @mock.patch('inspirehep.utils.knowledge.kb_mapping_exists')
    def test_check_keys_no_mapping(self, kb_m_e):
        kb_m_e.return_value = False

        from inspirehep.utils.knowledge import check_keys

        self.assertFalse(check_keys('kb', ['foo', 'bar']))

    @mock.patch('inspirehep.utils.knowledge.kb_mapping_exists')
    def test_check_keys_in_one_mapping(self, kb_m_e):
        kb_m_e.side_effect = [False, True]

        from inspirehep.utils.knowledge import check_keys

        self.assertTrue(check_keys('kb', ['foo', 'bar']))

    @mock.patch('inspirehep.utils.knowledge.add_kb_mapping')
    @mock.patch('inspirehep.utils.knowledge.check_keys')
    def test_save_keys_to_kb_all_new_keys(self, c_k, add_kb_m):
        c_k.return_value = False

        from inspirehep.utils.knowledge import save_keys_to_kb

        save_keys_to_kb('kb', ['foo', 'bar'], 'baz')

        add_kb_m.has_calls([
            ('kb', 'foo', 'baz'),
            ('kb', 'bar', 'baz')
        ])

    @mock.patch('inspirehep.utils.knowledge.add_kb_mapping')
    @mock.patch('inspirehep.utils.knowledge.get_value')
    @mock.patch('inspirehep.utils.knowledge.check_keys')
    def test_save_keys_to_kb_one_old_key(self, c_k, g_v, add_kb_m):
        c_k.return_value = True
        g_v.return_value = 'quux'

        from inspirehep.utils.knowledge import save_keys_to_kb

        save_keys_to_kb('kb', ['foo', 'bar'], 'baz')

        add_kb_m.has_calls([
            ('kb', 'foo', 'quux'),
            ('kb', 'bar', 'quux')
        ])

    def test_get_mappings_from_kbname_from_cache(self):
        from inspirehep.utils.knowledge import get_mappings_from_kbname

        cache = {
            'kb': [
                ('foo', 'foo'),
                ('bar', 'bar')
            ]
        }

        expected = [('foo', 'foo'), ('bar', 'bar')]
        result = get_mappings_from_kbname('kb', cache=cache)

        self.assertEqual(expected, result)

    @mock.patch('inspirehep.utils.knowledge.KnwKBRVAL.query_kb_mappings')
    @mock.patch('inspirehep.utils.knowledge.get_kb_by_name')
    def test_get_mappings_from_kbname(self, g_kb_b_n, K_q_kb_m):
        KB = namedtuple('KB', 'id')
        Mapping = namedtuple('Mapping', 'm_key, m_value')

        g_kb_b_n.return_value = KB('kb')
        K_q_kb_m.return_value = [
            Mapping('foo', 'foo'),
            Mapping('bar', 'bar')
        ]

        from inspirehep.utils.knowledge import get_mappings_from_kbname

        expected = [('foo', 'foo'), ('bar', 'bar')]
        result = get_mappings_from_kbname('kb')

        self.assertEqual(expected, result)
