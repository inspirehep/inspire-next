# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

"""Tests for the version."""

from helpers import reimport_module

from invenio_testing import InvenioTestCase

import mock


class VersionTests(InvenioTestCase):

    """Tests for the version."""

    @mock.patch('inspirehep.version.git_revision', return_value='19930202060000')
    def test_build_version(self, git_revision):
        """build_version conforms to PEP440."""
        from inspirehep.version import build_version

        self.assertEqual(build_version(1, 0, 0), '1.0')
        self.assertEqual(build_version(1, 1, 1), '1.1.1')
        self.assertEqual(build_version(1, 2, 3, 4), '1.2.3.4')
        self.assertEqual(build_version(2, 0, 0, 'dev', 1), '2.0.dev1')
        self.assertEqual(build_version(2, 0, 0, 'dev'), '2.0.dev19930202060000')
        self.assertEqual(build_version(2, 0, 1, 'dev'), '2.0.1.dev19930202060000')
        self.assertEqual(build_version(1, 2, 3, 4, 5, 6, 'dev'), '1.2.3.4.5.6.dev19930202060000')

    @mock.patch('inspirehep.version.subprocess.Popen')
    def test_git_revision_valid_date(self, popen):
        """git_revision extracts a valid date."""
        version = reimport_module('inspirehep.version')

        class MockCall(object):
            def communicate(self):
                return ['728632800', 'banana']

        popen.return_value = MockCall()

        self.assertEqual('19930202060000', version.git_revision())

    @mock.patch('inspirehep.version.subprocess.Popen')
    def test_git_revision_invalid_date(self, popen):
        """git_revision outputs 0 on an invalid date."""
        version = reimport_module('inspirehep.version')

        class MockCall(object):
            def communicate(self):
                return ['banana', 'banana']

        popen.return_value = MockCall()

        self.assertEqual('0', version.git_revision())

    def test_git_revision_from_cache(self):
        """git_revision fetches from its cache when possible."""
        version = reimport_module('inspirehep.version')

        version.git_revision._cache = '19930202060000'

        self.assertEqual('19930202060000', version.git_revision())
