# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Signal receivers for dealing with caching."""

from inspirehep.modules.citations.signals import after_citation_count_update

from invenio_records.signals import after_record_index

from .tasks import invalidate_cache_on_citation_count_update, invalidate_cache_on_record_index


@after_citation_count_update.connect
def invalidate_on_citation_count_update(recid, *args, **kwargs):
    # wait 3 seconds to make sure record with updated citation_count can be accessed from ES
    invalidate_cache_on_citation_count_update.apply_async(args=[recid], countdown=3)


@after_record_index.connect
def invalidate_on_record_index(recid, *args, **kwargs):
    # wait 3 seconds to make sure indexed record can be accessed from ES
    invalidate_cache_on_record_index.apply_async(args=[recid], countdown=3)
