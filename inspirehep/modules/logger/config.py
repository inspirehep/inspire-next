# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, division, print_function

import logging
import sys

from celery.signals import setup_logging

# Celery config
# ==============
@setup_logging.connect
def setup_basic_logging(*args, **kwargs):
    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=logging.INFO
    )


# Sentry config
# ==============
SENTRY_DSN = None
"""sentry domain"""

SENTRY_SEND_DEFAULT_PII = False
"""enable sending sensitive information to sentry"""
