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

from flask import current_app

from inspirehep.modules.search.api import JournalsSearch


def normalize_journal_title(journal_title):
    normalized_journal_title = journal_title
    hits = JournalsSearch().query(
        'match',
        lowercase_journal_titles=journal_title
    ).execute()

    if hits:
        try:
            normalized_journal_title = hits[0].short_title
        except (AttributeError, IndexError):
            current_app.logger.debug(
                "Failed to normalize journal title in: %s", repr(hits[0])
            )
    return normalized_journal_title
