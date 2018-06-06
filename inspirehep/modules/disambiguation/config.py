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

"""Disambiguation configuration."""

from __future__ import absolute_import, division, print_function


DISAMBIGUATION_CLUSTERS_PATH = '/tmp/clusters.json'
"""The path to the file that will store the curated clusters."""

DISAMBIGUTATION_PUBLICATIONS_PATH = '/tmp/publications.json'
"""The path to the file that will store the publication."""

DISAMBIGUATION_SIGNATURES_PATH = '/tmp/signatures.jl'
"""The path to the file that will store the curated signatures."""

DISAMBIGUATION_MODEL_PATH = '/tmp/inspire-disambiguation-model.pkl'
"""The path to the model that will be used to run the disambiguation."""

DISAMBIGUATION_ETHNICITY_DATA_PATH = '/tmp/ethnicity.csv'
"""The path to the data used to train the ethnicity estimator model."""

DISAMBIGUATION_ETHNICITY_MODEL_PATH = '/tmp/ethnicity.pkl'
"""The path to the trained ethnicity estimator model."""
