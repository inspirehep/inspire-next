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

"""Common functions used to mock."""

from __future__ import absolute_import, division, print_function

import os
import pkg_resources


def fake_download_file(workflow, name, url):
    """Mock download_file_to_workflow func."""
    if url == 'https://arxiv.org/e-print/1407.7587':
        workflow.files[name] = pkg_resources.resource_stream(
            __name__,
            os.path.join(
                '../fixtures',
                '1407.7587v1'
            )
        )
        return workflow.files[name]
    elif url == 'https://arxiv.org/pdf/1407.7587':
        workflow.files[name] = pkg_resources.resource_stream(
            __name__,
            os.path.join(
                '../fixtures',
                '1407.7587v1.pdf',
            )
        )
        return workflow.files[name]
    raise Exception("Download file not mocked!")


def fake_classifier_api_request(url, data):
    """Mock json_api_request func."""
    return {
        'prediction': 'non_core',
        'scores': {
            'core': 0.33398324251174927,
            'non_core': 0.6497962474822998,
            'rejected': 0.016220496967434883
        }
    }


def fake_magpie_api_request(url, data):
    """Mock json_api_request func."""
    if data.get('corpus') == "experiments":
        return {
            "labels": [
                ["CMS", 0.75495152473449707],
                ["GEMS", 0.45495152473449707],
                ["ALMA", 0.39597576856613159],
                ["XMM", 0.28373843431472778],
            ],
            "status_code": 200
        }
    elif data.get('corpus') == "categories":
        return {
            "labels": [
                ["Astrophysics", 0.9941025972366333],
                ["Phenomenology-HEP", 0.0034253709018230438],
                ["Instrumentation", 0.0025460966862738132],
                ["Gravitation and Cosmology", 0.0017545684240758419],
            ],
            "status_code": 200
        }
    elif data.get('corpus') == "keywords":
        return {
            "labels": [
                ["galaxy", 0.29424679279327393],
                ["numerical calculations", 0.22625420987606049],
                [
                    "numerical calculations: interpretation of experiments",
                    0.031719371676445007
                ],
                ["luminosity", 0.028066780418157578],
                ["experimental results", 0.027784878388047218],
                ["talk", 0.023392116650938988],
            ],
            "status_code": 200
        }
