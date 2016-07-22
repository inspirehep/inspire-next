# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Contains signal receivers for HEP dojson processing."""

from __future__ import absolute_import, division, print_function

from itertools import chain

from invenio_records.signals import before_record_insert, before_record_update

from inspirehep.utils.date import create_earliest_date
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_value


@before_record_insert.connect
@before_record_update.connect
def earliest_date(sender, *args, **kwargs):
    """Find and assign the earliest date to a HEP paper."""
    date_paths = [
        'preprint_date',
        'thesis.date',
        'thesis.defense_date',
        'publication_info.year',
        'creation_modification_date.creation_date',
        'imprints.date',
    ]

    dates = list(chain.from_iterable(
        [force_force_list(get_value(sender, path)) for path in date_paths]))

    earliest_date = create_earliest_date(dates)
    if earliest_date:
        sender['earliest_date'] = earliest_date
