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

from __future__ import absolute_import, division, print_function

import mock

from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
)


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.is_pdf_link'
)
def get_halted_workflow(mocked_is_pdf_link, app, record, extra_config=None):
    mocked_is_pdf_link.return_value = True

    extra_config = extra_config or {}
    with mock.patch.dict(app.config, extra_config):
        workflow_uuid = start('article', [record])

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]

    assert obj.status == ObjectStatus.HALTED
    assert obj.data_type == "hep"

    # Files should have been attached (tarball + pdf, and plots)
    assert obj.files["1407.7587.pdf"]
    assert obj.files["1407.7587.tar.gz"]

    assert len(obj.files) > 2

    # A publication note should have been extracted
    pub_info = obj.data.get('publication_info')
    assert pub_info
    assert pub_info[0]
    assert pub_info[0].get('year') == 2014
    assert pub_info[0].get('journal_title') == "J. Math. Phys."

    # A prediction should have been made
    prediction = obj.extra_data.get("relevance_prediction")
    assert prediction
    assert prediction['decision'] == 'Non-CORE'
    assert prediction['scores']['Non-CORE'] == 0.8358207729691823

    expected_experiment_prediction = {
        'experiments': [
            {'label': 'CMS', 'score': 0.75495152473449707}
        ]
    }
    experiments_prediction = obj.extra_data.get("experiments_prediction")
    assert experiments_prediction == expected_experiment_prediction

    keywords_prediction = obj.extra_data.get("keywords_prediction")
    assert keywords_prediction
    assert {
        "label": "galaxy",
        "score": 0.29424679279327393,
        "accept": True
    } in keywords_prediction['keywords']

    # This record should not have been touched yet
    assert "approved" not in obj.extra_data

    return workflow_uuid, eng, obj
