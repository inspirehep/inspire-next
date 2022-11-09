# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, division, print_function

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration

LOGGER = logging.getLogger(__name__)


class InspireLogger:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        # clear default handlers
        app.logger.handlers = []
        self.init_sentry(app)
        app.extensions["inspirehep-logger"] = self
        app.logger.propagate = True
        return self

    def init_sentry(self, app):
        sentry_dsn = app.config.get("SENTRY_DSN")

        if not sentry_dsn:
            LOGGER.debug("Sentry is not enabled for {}.".format(app.name))
            return

        send_default_pii = app.config.get("SENTRY_SEND_DEFAULT_PII", False)
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration(), CeleryIntegration()],
            send_default_pii=send_default_pii,
            release=os.environ.get("VERSION"),
        )

        LOGGER.debug("Sentry is initialized.")
