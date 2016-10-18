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

"""INSPIREHEP WSGI app instantiation with support for coverage.py.

Uses the trick in http://stackoverflow.com/a/20689873/1407497 to instantiate
a WSGI application that reports back information on test coverage.
"""

from __future__ import absolute_import, division, print_function

import atexit
import sys
from flask import (jsonify, request)

from inspirehep.modules.literaturesuggest.views import validate

import coverage

cov = coverage.Coverage(data_suffix=True)
cov.start()
from .wsgi import application  # noqa


def save_coverage():
    cov.stop()
    cov.save()

atexit.register(save_coverage)

app = getattr(application, 'app', application)

app.url_map._rules.remove(app.url_map._rules_by_endpoint['inspirehep_literature_suggest.validate'][0])
del app.view_functions['inspirehep_literature_suggest.validate']
del app.url_map._rules_by_endpoint['inspirehep_literature_suggest.validate']
app.url_map.update()


@app.route('/submit/literature/validate', endpoint='inspirehep_literature_suggest.validate', methods=['POST'])
def mock_literature_validate():
    """"Mock the pdf arXiv and DOI validation"""
    if 'url' in request.json:
        if request.json['url'] == 'pdf_url_correct':
            return '{"messages":{"url":{}}}'
        if request.json['url'] == 'pdf_url_wrong':
            return '{"messages":{"url":{"messages":["Please, provide an accessible direct link to a PDF document."],"state":"error"}}}'

    if 'arxiv_id' in request.json:
        if request.json['arxiv_id'] in ('1001.4538', 'hep-th/9711200'):
            return ''
        if request.json['arxiv_id'] == '-th.9711200':
            return '{"messages":{"arxiv_id":{"messages":["The provided ArXiv ID is invalid - it should look similar to \'hep-th/9711200\' or \'1207.7235\'."],"state":"error"}}}'

    if 'doi' in request.json:
        if request.json['doi'] in ('10.1086/305772', 'doi:10.1086/305772'):
            return ''
        if request.json['doi'] == 'dummy:10.1086/305772':
            return '{"messages":{"doi":{"messages":["The provided DOI is invalid - it should look similar to \'10.1086/305772\'."],"state":"error"}}}'

    return validate()
