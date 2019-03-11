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

import logging
import pkg_resources
from subprocess import check_output


logger = logging.getLogger(__name__)


def get_git_tag_version():
    try:
        return check_output('git log -1 --pretty=format:%H'.split())
    except Exception:
        git_repo_path = pkg_resources.get_distribution('inspirehep').location
        logger.error(
            'Error reading ``SHA`` from path "{}".'.format(git_repo_path)
        )
        return -1


__version__ = '0.1.0'
