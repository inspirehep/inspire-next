# -*- coding: utf-8 -*-

"""inspirehep Invenio WSGI application."""

from __future__ import absolute_import, print_function

from inspirehep.factory import create_app

application = create_app()

if application.debug:
    # apply Werkzeug WSGI middleware
    from werkzeug.debug import DebuggedApplication
    application = DebuggedApplication(application, evalex=True)
