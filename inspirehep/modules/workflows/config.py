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

"""Workflows configuration."""

from __future__ import absolute_import, division, print_function


WORKFLOWS_REFEXTRACT_TIMEOUT = 10 * 60
"""Time in seconds a refextract task is allowed to run before it is killed."""

WORKFLOWS_PLOTEXTRACT_TIMEOUT = 5 * 60
"""Time in seconds a plotextract task is allowed to run before it is killed."""
WORKFLOWS_MAX_AUTHORS_COUNT_FOR_GROBID_EXTRACTION = 50

WORKFLOWS_DOWNLOAD_DOCUMENT_TIMEOUT = 5 * 60
WORKFLOWS_DELETE_KEYS_TIMEOUT = 2 * 60
