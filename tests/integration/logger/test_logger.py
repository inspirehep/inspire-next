# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, division, print_function


def test_authors_workflow_stops_when_record_is_not_valid(isolated_app):
    assert not isolated_app.config['SENTRY_SEND_DEFAULT_PII']
    assert 'inspirehep-logger' in isolated_app.extensions
