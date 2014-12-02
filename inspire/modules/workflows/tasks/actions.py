# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from functools import wraps


def was_approved(obj, eng):
    """Check if the record was approved."""
    return obj.extra_data.get("approved", False)


def add_core(metadata):
    """Check if the record was approved as CORE."""
    collections = metadata.get("collections", [])
    # Do not add it again if already there
    has_core = [v for c in collections
                for v in c.values()
                if v.lower() == "core"]
    if not has_core:
        collections.append({"primary": "CORE"})
        metadata["collections"] = collections
    return metadata


def add_core_deposit(obj, eng):
    """Check if the record was approved as CORE."""
    from invenio.modules.deposit.models import Deposition
    if obj.extra_data.get("core"):
        d = Deposition(obj)
        sip = d.get_latest_sip(d.submitted)
        sip.metadata = add_core(sip.metadata)
        d.update()


def add_core_oaiharvest(obj, eng):
    """Check if the record was approved as CORE."""
    if obj.extra_data.get("core"):
        obj.data = add_core(obj.data)


def reject_record(message):
    """Reject record with message."""
    @wraps(reject_record)
    def _reject_record(obj, eng):
        obj.extra_data["approved"] = False
        obj.extra_data["reason"] = message
        obj.log.info(message)
    return _reject_record
