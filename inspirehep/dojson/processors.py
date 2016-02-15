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

    from inspirehep.dojson.utils import strip_empty_values
    from inspirehep.dojson.hep import hep
    from inspirehep.dojson.institutions import institutions
    from inspirehep.dojson.journals import journals
    from inspirehep.dojson.experiments import experiments
    from inspirehep.dojson.hepnames import hepnames
    from inspirehep.dojson.jobs import jobs
    from inspirehep.dojson.conferences import conferences

    for data in split_blob(source.read()):
        record = create_record(data)
        if _collection_in_record(record, 'institution'):
            yield strip_empty_values(institutions.do(record))
        elif _collection_in_record(record, 'experiment'):
            yield strip_empty_values(experiments.do(record))
        elif _collection_in_record(record, 'journals'):
            yield strip_empty_values(journals.do(record))
        elif _collection_in_record(record, 'hepnames'):
            yield strip_empty_values(hepnames.do(record))
        elif _collection_in_record(record, 'job') or \
                _collection_in_record(record, 'jobhidden'):
            yield strip_empty_values(jobs.do(record))
        elif _collection_in_record(record, 'conferences'):
            yield strip_empty_values(conferences.do(record))
        else:
            yield strip_empty_values(hep.do(record))


def _collection_in_record(record, collection):
    """Returns True if record is in collection"""
    colls = force_list(record.get("980__", []))
    for coll in colls:
        coll = coll.get('a', [])
        if isinstance(coll, list):
            if collection in [c.lower() for c in coll]:
                return True
        elif coll.lower() == collection:
            return True
    return False
