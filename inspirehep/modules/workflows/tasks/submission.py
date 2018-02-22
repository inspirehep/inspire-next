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

"""Contains INSPIRE specific submission tasks."""

from __future__ import absolute_import, division, print_function

import os
import logging
from functools import wraps
from pprint import pformat

from flask import current_app

from inspire_dojson import record2marcxml
from inspirehep.utils.robotupload import make_robotupload_marcxml


from .actions import in_production_mode
from ..utils import with_debug_logging

LOGGER = logging.getLogger(__name__)


def send_robotupload(
    url=None,
    callback_url="callback/workflows/robotupload",
    mode="insert",
    extra_data_key=None
):
    """Get the MARCXML from the model and ship it.

    If callback_url is set the workflow will halt and the callback is
    responsible for resuming it.
    """
    @with_debug_logging
    @wraps(send_robotupload)
    def _send_robotupload(obj, eng):
        combined_callback_url = ''
        if callback_url:
            combined_callback_url = os.path.join(
                current_app.config["SERVER_NAME"],
                callback_url
            )
            if not combined_callback_url.startswith('http'):
                combined_callback_url = "https://{0}".format(
                    combined_callback_url
                )

        if extra_data_key is not None:
            data = obj.extra_data.get(extra_data_key) or {}
        else:
            data = obj.data
        marcxml = record2marcxml(data)

        if current_app.debug:
            # Log what we are sending
            LOGGER.debug(
                "Going to robotupload mode:%s to url:%s:\n%s\n",
                mode,
                url,
                marcxml,
            )

        if not in_production_mode():
            obj.log.debug(
                "Going to robotupload %s to %s:\n%s\n",
                mode,
                url,
                marcxml,
            )
            obj.log.debug(
                "Base object data:\n%s",
                pformat(data)
            )
            return

        result = make_robotupload_marcxml(
            url=url,
            marcxml=marcxml,
            callback_url=combined_callback_url,
            mode=mode,
            nonce=obj.id,
            priority=5,
        )
        if "[INFO]" not in result.text:
            if "cannot use the service" in result.text:
                # IP not in the list
                obj.log.error("Your IP is not in "
                              "app.config_BATCHUPLOADER_WEB_ROBOT_RIGHTS "
                              "on host: %s", result.text)
            txt = "Error while submitting robotupload: {0}".format(result.text)
            raise Exception(txt)
        else:
            obj.log.info("Robotupload sent!")
            obj.log.info(result.text)
            if callback_url:
                eng.halt("Waiting for robotupload: {0}".format(result.text))

        obj.log.info("end of upload")

    return _send_robotupload


@with_debug_logging
def wait_webcoll(obj, eng):
    if not in_production_mode():
        obj.log.debug("Would have wait for webcoll callback.")
        return

    eng.halt("Waiting for webcoll.")


@with_debug_logging
def filter_keywords(obj, eng):
    """Removes non-accepted keywords from the metadata"""
    prediction = obj.extra_data.get('keywords_prediction', {})
    if prediction:
        keywords = prediction.get('keywords')

        keywords = filter(lambda x: x['accept'], keywords)
        obj.extra_data['keywords_prediction']['keywords'] = keywords

        obj.log.debug('Filtered keywords: \n%s', pformat(keywords))

    obj.log.debug('Got no prediction for keywords')


@with_debug_logging
def prepare_keywords(obj, eng):
    """Prepares the keywords in the correct format to be sent"""
    prediction = obj.extra_data.get('keywords_prediction', {})
    if not prediction:
        return

    keywords = obj.data.get('keywords', [])
    for keyword in prediction.get('keywords', []):
        # TODO: differentiate between curated and gueesed keywords
        keywords.append(
            {
                'value': keyword['label'],
                'source': 'curator' if keyword.get('curated') else 'magpie',
            }
        )

    obj.data['keywords'] = keywords

    obj.log.debug('Finally got keywords: \n%s', pformat(keywords))


@with_debug_logging
def remove_references(obj, eng):
    obj.log.info(obj.data)
    if 'references' in obj.data:
        del obj.data['references']
