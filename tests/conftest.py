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

"""Pytest configuration."""

import os
import shutil
import tempfile
import pytest
import six

from flask_celeryext import FlaskCeleryExt
from invenio_mail import InvenioMail
from inspirehep.factory import create_app


if six.PY2:
    from StringIO import StringIO
else:
    from io import StringIO


@pytest.yield_fixture(scope='session', autouse=True)
def email_app(request):
    """Email-aware Flask application fixture."""
    app = create_app(
        CFG_SITE_SUPPORT_EMAIL='admin@inspirehep.net',
        INSPIRELABS_FEEDBACK_EMAIL='labsfeedback@inspirehep.net',
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        MAIL_SUPPRESS_SEND=True,
    )
    FlaskCeleryExt(app)

    InvenioMail(app, StringIO())

    with app.app_context():
        yield app


@pytest.yield_fixture(scope='session', autouse=True)
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()

    os.environ.update(
        APP_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )

    app = create_app(
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
    )

    def teardown():
        shutil.rmtree(instance_path)

    request.addfinalizer(teardown)

    with app.app_context():
        yield app
