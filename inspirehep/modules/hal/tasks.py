# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from celery import shared_task
from flask import current_app

from invenio_db import db
from inspirehep.utils.record import get_value
from inspirehep.modules.hal.tei import tei_response
from inspirehep.modules.hal import hal_api

from .models import InspireHalRecords

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

DATE_FORMAT = "%a, %d %b %Y %X %Z"


def doc_type_should_be_sent_to_hal(record):
    """If the record has at least one institution with a halID, return True."""
    # FIXME: Figure out how to check if institutions are in HAL
    return False


#@shared_task(ignore_result=True)
def send_to_hal(sender, inspire_id, attachment=None):
    """Sends records to hal."""
    if True:#doc_type_should_be_sent_to_hal(sender):
        logger.info("Sending to hal: ", inspire_id)
        try:
            hal_tei = tei_response(sender, attachment)
            receipt = hal_api.add_record(hal_tei, attachment)
            hal_log_record = InspireHalRecords(
                inspire_id = inspire_id,
                hal_id = receipt.id,
                version = 1,
                date = datetime.strptime(receipt.response_headers['date'], DATE_FORMAT)
            )
            with db.session.begin_nested():
                db.session.add(hal_log_record)
            db.session.commit()
            logger.info("Successfully sent to hal: ",
                        receipt.id)
        except Exception as e:
            print e.response.text, id
            logger.error("Failed to push to hal: ", id)

