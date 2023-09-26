# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2023 CERN.
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

from celery import bootsteps
from celery.signals import worker_ready, worker_shutdown
from flask_celeryext import AppContextTask, create_celery_app
from psycopg2 import OperationalError as Psycopg2OperationalError
from sqlalchemy.exc import InvalidRequestError, OperationalError

from inspirehep.factory import create_app


HEARTBEAT_FILE = "/tmp/celery_live"
READINESS_FILE = "/tmp/celery_ready"

LOGGER = logging.getLogger(__name__)


class CeleryTask(AppContextTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(
            exc, (InvalidRequestError, OperationalError, Psycopg2OperationalError)
        ):
            LOGGER.exception("Shutting down celery process because of".format(exc))
            try:
                with open("/dev/termination-log", "w") as term_log:
                    term_log.write(str(exc))
            finally:
                os.kill(os.getppid(), signal.SIGTERM)


# adapted from https://github.com/celery/celery/issues/4079#issuecomment-1128954283
class LivenessProbe(bootsteps.StartStopStep):
    requires = {"celery.worker.components:Timer"}

    def __init__(self, worker, **kwargs):
        self.requests = []
        self.tref = None

    def start(self, worker):
        self.tref = worker.timer.call_repeatedly(
            1.0,
            self.update_heartbeat_file,
            (worker,),
            priority=10,
        )

    def stop(self, worker):
        try:
            os.remove(HEARTBEAT_FILE)
        except OSError:
            pass

    def update_heartbeat_file(self, worker):
        if not os.path.exists(READINESS_FILE):
            open(HEARTBEAT_FILE, 'w').close()


@worker_ready.connect
def worker_ready(**_):
    if not os.path.exists(READINESS_FILE):
        open(READINESS_FILE, 'w').close()


@worker_shutdown.connect
def worker_shutdown(**_):
    try:
        os.remove(READINESS_FILE)
    except OSError:
        pass


celery = create_celery_app(create_app(LOGGING_SENTRY_CELERY=True))
celery.Task = CeleryTask
celery.steps["worker"].add(LivenessProbe)

# We don't want to log to Sentry backoff errors
logging.getLogger("backoff").propagate = 0
