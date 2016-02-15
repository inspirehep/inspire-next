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

"""Tests for views"""

from invenio.testsuite import InvenioTestCase

import mock


# FIXME(jacquerie): should be in an helpers file.
mock_user = {'email': 'user@example.com'}

# FIXME(jacquerie): should be in an helpers file.
feedback_email_cfg = {
    'CFG_SITE_SUPPORT_EMAIL': 'support@inspirehep.net',
    'INSPIRELABS_FEEDBACK_EMAIL': 'feedback@inspirehep.net'
}


class ViewsTests(InvenioTestCase):
    """Tests views."""

    def test_detailed_records(self):
        """Test visiting each detailed record returns 200"""
        from invenio_records.models import Record

        self.login('admin', 'admin')  # To also check restricted records
        for recid in Record.allids():
            response = self.client.get("/record/{recid}".format(recid=recid))
            if response.status_code != 200:
                raise Exception(response, recid)

    def test_login(self):
        """Test visiting login page returns 200"""
        self.assertEqual(self.login('admin', 'admin').status_code, 200)

    def test_literature_landing_page(self):
        """Test visiting literature landing page returns 200"""
        self.assertEqual(self.client.get("/literature").status_code, 200)

    def test_conferences_landing_page(self):
        """Test visiting conferences landing page returns 200"""
        self.assertEqual(self.client.get("/conferences").status_code, 200)

    def test_jobs_landing_page(self):
        """Test jobs each landing page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get("/search?cc=jobs").status_code, 200)

    def test_institutions_landing_page(self):
        """Test visiting institutions landing page returns 200"""
        self.assertEqual(self.client.get("/institutions").status_code, 200)

    def test_experiments_landing_page(self):
        """Test visiting experiments landing page returns 200"""
        self.assertEqual(self.client.get("/experiments").status_code, 200)

    def test_journals_landing_page(self):
        """Test visiting journals landing page returns 200"""
        self.assertEqual(self.client.get("/journals").status_code, 200)

    def test_author_update(self):
        """Test visiting author update page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get(
            "/author/update?recid=997876").status_code, 200)

    def test_author_new(self):
        """Test visiting author new page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get("/author/new").status_code, 200)

    def test_literature_create(self):
        """Test visiting submit page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get(
            "/submit/literature/").status_code, 200)

    def test_holdingpen_list(self):
        """Test visiting holdingpen list page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get(
            "/admin/holdingpen/list").status_code, 200)

    def test_search(self):
        """Test visiting search page returns 200"""
        self.assertEqual(self.client.get("/search").status_code, 200)
        self.assertEqual(self.client.get(
            "/search?cc=HEP&p=&sf=earliest_date&so=desc&rg=25")
            .status_code, 200)
        self.assertEqual(self.client.get(
            "/search?cc=HEP&p=&sf=citation_count&so=desc&rg=100")
            .status_code, 200)
        self.assertEqual(self.client.get(
            "/search?cc=HEP&p=higgs&action_search=&sf=citation_count&so=desc&rg=100&post_filter=doc_type%3A'peer%20reviewed'")
            .status_code, 200)

    def test_doi_search(self):
        """Test visiting doi search page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get(
            "/doi/search?doi=10.1103/PhysRevLett.54.2580").status_code, 200)

    def test_arxiv_search(self):
        """Test visiting arxiv search page returns 200"""
        self.login('admin', 'admin')
        self.assertEqual(self.client.get(
            "/arxiv/search?arxiv=1506.03115").status_code, 200)

    @mock.patch('inspirehep.base.views.cfg', feedback_email_cfg)
    @mock.patch('inspirehep.base.views.send_email', return_value=True)
    def test_postfeedback_provided_email(self, send_email):
        """Accepts feedback when providing an email."""
        response = self.client.post('/postfeedback', data=dict(
            replytoaddr='user@example.com', feedback='foo bar'))

        send_email.assert_called_once_with(attachments=[],
            content='Feedback:\n\nfoo bar', fromaddr='support@inspirehep.net',
            replytoaddr='user@example.com', subject='INSPIRE Labs feedback',
            toaddr='feedback@inspirehep.net')

        self.assertEqual(response.status_code, 200)

    @mock.patch('inspirehep.base.views.current_user', mock_user)
    @mock.patch('inspirehep.base.views.cfg', feedback_email_cfg)
    @mock.patch('inspirehep.base.views.send_email', return_value=True)
    def test_postfeedback_logged_in_user(self, send_email):
        """Falls back to the email of the logged in user."""
        response = self.client.post('/postfeedback', data=dict(feedback='foo bar'))

        send_email.assert_called_once_with(attachments=[],
            content='Feedback:\n\nfoo bar', fromaddr='support@inspirehep.net',
            replytoaddr='user@example.com', subject='INSPIRE Labs feedback',
            toaddr='feedback@inspirehep.net')

        self.assertEqual(response.status_code, 200)

    def test_postfeedback_anonymous_user(self):
        """Rejects feedback without an email."""
        response = self.client.post('/postfeedback', data=dict(feedback='foo bar'))

        self.assertEqual(response.status_code, 403)

    @mock.patch('inspirehep.base.views.current_user', mock_user)
    def test_postfeedback_empty_feedback(self):
        """Rejects empty feedback."""
        response = self.client.post('/postfeedback', data=dict(feedback=''))

        self.assertEqual(response.status_code, 400)

    @mock.patch('inspirehep.base.views.cfg', feedback_email_cfg)
    @mock.patch('inspirehep.base.views.send_email', return_value=False)
    def test_postfeedback_send_email_failure(self, send_email):
        """Informs the user when a server error occurred."""
        response = self.client.post('/postfeedback', data=dict(
            replytoaddr='user@example.com', feedback='foo bar'))

        self.assertEqual(response.status_code, 500)
