# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""INSPIREHEP Celery app instantiation."""

from __future__ import absolute_import, division, print_function

import logging
import os
import signal

from flask_celeryext import AppContextTask, create_celery_app
from psycopg2 import OperationalError as Psycopg2OperationalError
from sqlalchemy.exc import InvalidRequestError, OperationalError

from inspirehep.factory import create_app


LOGGER = logging.getLogger(__name__)


class CeleryTask(AppContextTask):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(exc, (InvalidRequestError, OperationalError, Psycopg2OperationalError)):
            LOGGER.exception('Shutting down celery process because of'.format(exc))
            try:
                with open('/dev/termination-log', 'w') as term_log:
                    term_log.write(str(exc))
            finally:
                os.kill(os.getppid(), signal.SIGTERM)


celery = create_celery_app(create_app(LOGGING_SENTRY_CELERY=True))
celery.Task = CeleryTask

# We don't want to log to Sentry backoff errors
logging.getLogger('backoff').propagate = 0
