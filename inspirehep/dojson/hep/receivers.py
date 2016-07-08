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

from invenio_records.signals import before_record_insert, before_record_update

from inspirehep.utils.date import create_earliest_date


@before_record_insert.connect
@before_record_update.connect
def earliest_date(sender, *args, **kwargs):
    """Find and assign the earliest date to a HEP paper."""
    dates = []

    if 'preprint_date' in sender:
        dates.append(sender['preprint_date'])

    if 'thesis' in sender:
        if 'date' in sender['thesis']:
            dates.append(sender['thesis']['date'])
        if 'defense_date' in sender['thesis']:
            dates.append(sender['thesis']['defense_date'])

    if 'publication_info' in sender:
        for publication_info_key in sender['publication_info']:
            if 'year' in publication_info_key:
                dates.append(publication_info_key['year'])

    if 'creation_modification_date' in sender:
        for date in sender['creation_modification_date']:
            if 'creation_date' in date:
                dates.append(date['creation_date'])

    if 'imprints' in sender:
        for imprint in sender['imprints']:
            if 'date' in imprint:
                dates.append(imprint['date'])

    earliest_date = create_earliest_date(dates)
    if earliest_date:
        sender['earliest_date'] = earliest_date
