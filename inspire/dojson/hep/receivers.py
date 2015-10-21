# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Contains signal receivers for HEP dojson processing."""

from inspire.dojson import utils as inspire_dojson_utils

from invenio_records.signals import (
    before_record_insert,
    before_record_update,
)


@before_record_insert.connect
@before_record_update.connect
def earliest_date(sender, *args, **kwargs):
    """Find and assign the earliest date to a HEP paper."""
    dates = []

    if 'preprint_date' in sender:
        dates.append(sender['preprint_date'])

    if 'thesis' in sender:
        for thesis_key in sender['thesis']:
            if 'date' in thesis_key:
                dates.append(thesis_key['date'])
            if 'defense_date' in thesis_key:
                dates.append(thesis_key['defense_date'])

    if 'publication_info' in sender:
        for publication_info_key in sender['publication_info']:
            if 'year' in publication_info_key:
                dates.append(publication_info_key['year'])

    # Sort dates and pick the first one.
    dates.sort()

    if dates:
        sender['earliest_date'] = \
            inspire_dojson_utils.create_valid_date(dates[0])
