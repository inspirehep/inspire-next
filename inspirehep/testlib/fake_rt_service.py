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

"""Fake RT service module"""

from __future__ import absolute_import, division, print_function

import requests
from flask import Flask

from inspirehep.testlib.inspire_vcr import inspire_vcr as my_vcr


DEFAULT_CONFIG = {
    'DEBUG': True,
    'TESTING': True,
}


def create_fake_flask_app(config=DEFAULT_CONFIG):
    app = Flask(__name__)
    app.config.update(config)
    return app


application = create_fake_flask_app()


@application.route('/<args>')
def home(args):
    with my_vcr('rt_tickets').use_cassette('rt_request.yml'):
        resp = requests.get(args)
        return resp.text
