# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""Fake Legacy service module"""

from __future__ import absolute_import, division, print_function

import logging
import time

from flask import Flask, jsonify, request
from threading import Thread

from inspirehep.testlib.api_clients import (
    InspireApiClient,
    RobotuploadCallbackResult,
)

DEFAULT_CONFIG = {
    'DEBUG': True,
    'TESTING': True,
}


def create_fake_flask_app(config=DEFAULT_CONFIG):
    app = Flask(__name__)
    app.config.update(config)
    return app


application = create_fake_flask_app()


@application.route('/batchuploader/robotupload/<args>', methods=['POST'])
def robot_upload(args):
    wf_id = request.args['nonce']

    response = (
        'Robotupload sent!'
        '[INFO] some info'
        'end of upload'
    )
    logging.log(logging.INFO, msg='Got args {}'.format(args))
    logging.log(logging.INFO, msg='Responding {}'.format(response))

    t = Thread(target=do_callbacks, args=(wf_id))
    t.start()

    return response


def do_callbacks(workflow_id):
    server_name = application.config['SERVER_NAME']

    inspire_client = InspireApiClient(base_url='http://test-web-e2e.local:5000')
    hp_entry = inspire_client.holdingpen.get_detail_entry(workflow_id)

    response = inspire_client.callbacks.robotupload(
        nonce=workflow_id,
        results=[
            RobotuploadCallbackResult(
                recid=hp_entry.control_number,
                error_message="",
                success=True,
                marcxml="fake marcxml (not really used yet anywhere)",
                url="%s/record/%s" % (server_name, hp_entry.control_number),
            ),
        ],
    )
    assert response.status_code == 200

    time.sleep(2)

    response = inspire_client.callbacks.webcoll(
        recids=[hp_entry.control_number],
    )
    assert response.status_code == 200


@application.route('/batchuploader/allocaterecord', methods=['GET'])
def allocaterecord():
    return jsonify(42)
