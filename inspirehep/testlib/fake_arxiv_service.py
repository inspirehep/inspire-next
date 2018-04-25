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

"""Fake arXiv service module"""

from __future__ import absolute_import, division, print_function

import requests
import subprocess
import time

from flask import Flask

from inspirehep.testlib.inspire_vcr import inspire_vcr


DEFAULT_CONFIG = {
    'DEBUG': True,
    'TESTING': True,
}


def create_fake_flask_app(config=DEFAULT_CONFIG):
    app = Flask(__name__)
    app.config.update(config)
    return app


application = create_fake_flask_app()
my_vcr = inspire_vcr('arxiv')


@application.route('/')
def home():
    return '<h2>Fake arXiv service running...</h2>'


@application.route('/pdf/<arxiv_id>')
def pdf(arxiv_id):
    if not str(arxiv_id).endswith('.pdf'):
        arxiv_id = "{}.pdf".format(arxiv_id)

    url_request = 'https://arxiv.org/pdf/{}'.format(arxiv_id)
    with my_vcr.use_cassette('arxiv_single_pdf_cassette.yml'):
        resp = requests.get(url_request)
        return resp.text


@application.route('/e-print/<arxiv_id>')
def e_print(arxiv_id):
    url_request = 'https://arxiv.org/e-print/{}'.format(arxiv_id)
    with my_vcr.use_cassette('arxiv_single_tarball_cassette.yml'):
        resp = requests.get(url_request)
        return resp.text


@application.route('/oai2', methods=['GET'])
def oai_api():
    today = time.strftime("%Y-%m-%d")
    url_request = 'http://export.arxiv.org/oai2?verb=ListRecords&from={}&set=physics&metadataPrefix=arXivRaw'.format(today)

    with my_vcr.use_cassette('non_core_article.yml'):
        resp = requests.get(url_request)
        return resp.text


class FakeArxivService(object):
    """Service used to run arXiv harvest operations"""
    def __init__(self):
        # TODO: initialize here the scenario
        pass

    def run_harvest(self):
        """Run an arXiv harvest scheduling a job in celery"""
        # TODO: set self.harvest_scenario in the config for fake_arxiv_service
        run_harvest = 'inspirehep crawler schedule arXiv article --kwarg ' \
            'url=http://fake-arxiv:8888/oai2 --kwarg sets=physics,' \
            'hep-th --kwarg from_date=2018-03-25'

        assert subprocess.check_output(
            run_harvest.split(),
            stderr=subprocess.STDOUT
        )
