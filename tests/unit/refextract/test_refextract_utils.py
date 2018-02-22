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

from inspirehep.modules.refextract.utils import KbWriter


def test_kb_writer_two_entries(tmpdir):
    kb_file = tmpdir.join('two_entries.kb')

    with KbWriter(str(kb_file)) as writer:
        writer.add_entry('Journal of Testing', 'J.Testing')
        writer.add_entry('J.Testing', 'J.Testing')

    expected = [
        'JOURNAL OF TESTING---J.Testing\n',
        'J TESTING---J.Testing\n',
    ]

    assert expected == kb_file.readlines()


def test_kb_writer_unicode(tmpdir):
    kb_file = tmpdir.join('unicode.kb')

    with KbWriter(str(kb_file)) as writer:
        writer.add_entry(u'Journal de l\'Académie', 'J.Acad.')

    expected = [
        'JOURNAL DE L ACADÉMIE---J.Acad.\n',
    ]

    assert expected == kb_file.readlines()


def test_kb_writer_many_lines(tmpdir):
    kb_file = tmpdir.join('many_lines.kb')

    with KbWriter(str(kb_file)) as writer:
        for numlines in xrange(100000):
            writer.add_entry('Journal of Testing', 'J.Testing')

    assert len(kb_file.readlines()) == 100000


def test_kb_writer_multiple_runs(tmpdir):
    kb_file = tmpdir.join('multiple_flushes.kb')

    with KbWriter(str(kb_file)) as writer:
        writer.add_entry('Journal of Testing', 'J.Testing')

    with KbWriter(str(kb_file)) as writer:
        writer.add_entry('Second Journal of Testing', 'Sec.J.Testing')

    expected = [
        'SECOND JOURNAL OF TESTING---Sec.J.Testing\n',
    ]

    assert expected == kb_file.readlines()
