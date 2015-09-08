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
#

import uuid

from invenio_records.signals import (
    before_record_insert,
    before_record_update,
)


@before_record_insert.connect
@before_record_update.connect
def assign_uuid(sender, *args, **kwargs):
    """Assign uuid to each author of a HEP paper."""
    if 'authors' in sender:
        authors = sender['authors']

        for author in authors:
            if not 'uuid' in author:
                author['uuid'] = str(uuid.uuid4())

        sender['authors'] = authors

