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

"""Convert incoming MARCXML to JSON."""

from dojson.utils import force_list


def convert_marcxml(source):
    """Convert MARC XML to JSON."""
    from dojson.contrib.marc21.utils import create_record, split_blob

    from inspire.dojson.hep import hep
    from inspire.dojson.institutions import institutions
    from inspire.dojson.journals import journals
    from inspire.dojson.experiments import experiments

    for data in split_blob(source.read()):
        record = create_record(data)
        if _collection_in_record(record, 'institution'):
            yield institutions.do(record)
        elif _collection_in_record(record, 'experiment'):
            yield experiments.do(record)
        elif _collection_in_record(record, 'journals'):
            yield journals.do(record)
        else:
            yield hep.do(record)


def _collection_in_record(record, collection):
    """Return a list of collections (lowercased) from 980__a."""
    colls = force_list(record.get("980__", []))
    return collection in [
            coll.get('a', "").lower()
            for coll in colls if coll
        ]
