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

"""Unit tests for the function sending robotuploads."""

from invenio_testing import InvenioTestCase

import mock


# FIXME(jacquerie): should be in a helpers file.
robotupload_cfg = {'CFG_ROBOTUPLOAD_SUBMISSION_BASEURL': 'url_from_cfg'}


class RobotuploadTests(InvenioTestCase):

    """Unit tests for the function sending robotuploads."""

    def setup_class(self):
        self.clean_xml = 'data'
        self.user_agent = 'inspire'
        self.headers = {
            'User-agent': 'inspire',
            'Content-Type': 'application/marcxml+xml'
        }

    @mock.patch('inspirehep.utils.robotupload.clean_xml')
    @mock.patch('inspirehep.utils.robotupload.make_user_agent_string')
    @mock.patch('inspirehep.utils.robotupload.requests.post')
    def test_make_robotupload_marcxml_from_user(self, post, m_u_a_s, c_x):
        c_x.return_value = self.clean_xml
        m_u_a_s.return_value = self.user_agent

        from inspirehep.utils.robotupload import make_robotupload_marcxml

        make_robotupload_marcxml('url_from_user', 'banana', 'foo')
        post.assert_called_with(
            url='url_from_user/batchuploader/robotupload/foo',
            data='data',
            headers=self.headers,
            params={}
        )

    @mock.patch('inspirehep.utils.robotupload.clean_xml')
    @mock.patch('inspirehep.utils.robotupload.make_user_agent_string')
    @mock.patch('inspirehep.utils.robotupload.cfg', robotupload_cfg)
    @mock.patch('inspirehep.utils.robotupload.requests.post')
    def test_make_robotupload_marcxml_from_cfg(self, post, m_u_a_s, c_x):
        c_x.return_value = self.clean_xml
        m_u_a_s.return_value = self.user_agent

        from inspirehep.utils.robotupload import make_robotupload_marcxml

        make_robotupload_marcxml(None, 'banana', 'foo', bar='baz')
        post.assert_called_with(
            url='url_from_cfg/batchuploader/robotupload/foo',
            data='data',
            headers=self.headers,
            params={'bar': 'baz'}
        )

