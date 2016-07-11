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

"""Convert incoming MARCXML to JSON."""

from __future__ import absolute_import, division, print_function

from dojson.utils import force_list

from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.hep import hep
from inspirehep.dojson.hepnames import hepnames
from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.journals import journals
from inspirehep.dojson.utils import clean_record


def overdo_marc_dict(record):
    """Convert MARC Groupable Ordered Dict into JSON."""
    if _collection_in_record(record, 'institution'):
        return clean_record(institutions.do(record))
    elif _collection_in_record(record, 'experiment'):
        return clean_record(experiments.do(record))
    elif _collection_in_record(record, 'journals'):
        return clean_record(journals.do(record))
    elif _collection_in_record(record, 'hepnames'):
        return clean_record(hepnames.do(record))
    elif _collection_in_record(record, 'job') or \
            _collection_in_record(record, 'jobhidden'):
        return clean_record(jobs.do(record))
    elif _collection_in_record(record, 'conferences'):
        return clean_record(conferences.do(record))
    else:
        return clean_record(hep.do(record))


def _collection_in_record(record, collection):
    """Returns True if record is in collection"""
    colls = force_list(record.get("980__", []))
    for coll in colls:
        coll = force_list(coll.get('a', []))
        if collection in [c.lower() for c in coll]:
            return True
    return False
