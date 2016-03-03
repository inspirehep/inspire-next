# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Persistent identifier minters."""

from __future__ import absolute_import, print_function

from collections import namedtuple

from .providers import InspireRecordIdProvider

FetchedPID = namedtuple('FetchedPID', ['provider', 'pid_type', 'pid_value'])


def inspire_recid_fetcher(record_uuid, data):
    """Fetch a record's identifiers."""
    assert "$schema" in data
    return FetchedPID(
        provider=InspireRecordIdProvider,
        pid_type=InspireRecordIdProvider.schema_to_pid_type(data['$schema']),
        pid_value=str(data['control_number']),
    )
