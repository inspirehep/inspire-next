# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, division, print_function

import mock
from flask import Flask

from inspirehep.modules.logger import InspireLogger


@mock.patch("inspirehep.modules.logger.ext.sentry_sdk.init")
def test_ext_with_dsn(mock_sentry_sdk):
    SENTRY_DSN = "TEST_DSN_URL_FOR_SENTRY"
    SENTRY_SEND_DEFAULT_PII = True

    app = Flask("testapp")
    app.config.update(
        {"SENTRY_DSN": SENTRY_DSN, "SENTRY_SEND_DEFAULT_PII": SENTRY_SEND_DEFAULT_PII}
    )
    InspireLogger(app)
    mock_sentry_sdk.assert_called_once()


@mock.patch("inspirehep.modules.logger.ext.sentry_sdk.init")
def test_ext_without_dsn(mock_sentry_sdk):
    SENTRY_DSN = None
    SENTRY_SEND_DEFAULT_PII = True

    app = Flask("testapp")
    app.config.update(
        {"SENTRY_DSN": SENTRY_DSN, "SENTRY_SEND_DEFAULT_PII": SENTRY_SEND_DEFAULT_PII}
    )
    InspireLogger(app)
    mock_sentry_sdk.assert_not_called()
