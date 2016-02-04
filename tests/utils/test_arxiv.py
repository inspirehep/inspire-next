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

"""Test helpers for arXiv.org."""

from invenio_base.wrappers import lazy_import
from invenio_testing import InvenioTestCase

import mock

Record = lazy_import('invenio_records.api.Record')


class ArXivTests(InvenioTestCase):

    """Test helpers for arXiv.org."""

    @mock.patch('inspirehep.utils.arxiv.download_file')
    def test_get_tarball(self, download_file):
        """Examples taken from https://arxiv.org/help/arxiv_identifier."""
        from inspirehep.utils.arxiv import get_tarball

        get_tarball('1501.00001', '/tmp')
        download_file.assert_called_with(
            'http://arxiv.org/e-print/1501.00001',
            '/tmp/1501.00001.tar.gz'
        )

        get_tarball('1501.00001v1', '/tmp')
        download_file.assert_called_with(
            'http://arxiv.org/e-print/1501.00001v1',
            '/tmp/1501.00001v1.tar.gz'
        )

        get_tarball('math.GT/0309136', '/tmp')
        download_file.assert_called_with(
            'http://arxiv.org/e-print/math.GT/0309136',
            '/tmp/math.GT_0309136.tar.gz'
        )

    @mock.patch('inspirehep.utils.arxiv.download_file')
    def test_get_pdf(self, download_file):
        """Examples taken from https://arxiv.org/help/arxiv_identifier."""
        from inspirehep.utils.arxiv import get_pdf

        get_pdf('0706.0001', '/tmp')
        download_file.assert_called_with(
            'http://arxiv.org/pdf/0706.0001',
            '/tmp/0706.0001.pdf'
        )

        get_pdf('0706.0001v2', '/tmp')
        download_file.assert_called_with(
            'http://arxiv.org/pdf/0706.0001v2',
            '/tmp/0706.0001v2.pdf'
        )

        get_pdf('math.GT/0309136', '/tmp')
        download_file.assert_called_with(
            'http://arxiv.org/pdf/math.GT/0309136',
            '/tmp/math.GT_0309136.pdf'
        )

    def test_get_arxiv_id_from_record_with_arxiv_id(self):
        """Return arxiv_id of a record, if present."""
        from inspirehep.utils.arxiv import get_arxiv_id_from_record

        with_arxiv_id = Record({'arxiv_id': '1501.00001'})

        expected = '1501.00001'
        result = get_arxiv_id_from_record(with_arxiv_id)

        self.assertEqual(expected, result)

    def test_get_arxiv_id_from_record_with_arxiv_eprint(self):
        """Return arxiv_eprint of a record, if present."""
        from inspirehep.utils.arxiv import get_arxiv_id_from_record

        with_eprint = Record({'arxiv_eprints': [{'value': '1501.00001'}]})

        expected = '1501.00001'
        result = get_arxiv_id_from_record(with_eprint)

        self.assertEqual(expected, result)

    def test_get_arxiv_id_from_record_with_arxiv_eprints_selects_last(self):
        """Return last arxiv_eprint of a record."""
        from inspirehep.utils.arxiv import get_arxiv_id_from_record

        with_eprints = Record({
            'arxiv_eprints': [
                {'value': '1501.00001'},
                {'value': '1501.00001v1'}
            ]
        })

        expected = '1501.00001v1'
        result = get_arxiv_id_from_record(with_eprints)

        self.assertEqual(expected, result)

    def test_get_arxiv_id_from_record_removes_prefix(self):
        """Remove prefix of selected arxiv_id."""
        from inspirehep.utils.arxiv import get_arxiv_id_from_record

        with_prefix = Record({'arxiv_id': 'arXiv:1501.00001'})

        expected = '1501.00001'
        result = get_arxiv_id_from_record(with_prefix)

        self.assertEqual(expected, result)
