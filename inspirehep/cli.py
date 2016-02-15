# -*- coding: utf-8 -*-

"""inspirehep base Invenio configuration."""

from __future__ import absolute_import, print_function

from invenio_base.app import create_cli

from .factory import create_app

cli = create_cli(create_app=create_app)
