# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

""" Configuration of authors module."""

from invenio.config import CFG_SITE_URL

# Record definition variables

AUTHORS_IDENTIFIERS_TYPES = ['authorid', 'orcid', 'arxiv']

AUTHORS_AFFILIATION_STATUS = ['current']
AUTHORS_EXPERIMENT_STATUS = ['current']
AUTHORS_EMAIL_STATUS = ['current']

AUTHORS_NAME_NUMERATIONS = "^Jr\.|Sr\.|I{1,3}|IV|VI{0,3}$"
AUTHORS_NAME_STATUSES = ['active', 'deceased', 'departed', 'retired']
AUTHORS_NAME_TITLES = ['Sir']

AUTHORS_AFFILIATION_RANKS = ['senior', 'junior', 'staff', 'visitor', 'postdoc',
                             'phd', 'masters', 'undergrad']

# Author new/update form

AUTHORS_UPDATE_BASE_URL = CFG_SITE_URL
""" URL used to prefill author update form """
