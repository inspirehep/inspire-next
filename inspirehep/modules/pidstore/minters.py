# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Persistent identifier minters."""

from __future__ import absolute_import, division, print_function

import abc
from flask import current_app
import six

from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from .exceptions import DuplicatedPIDMinterException
from .providers import InspireRecordIdProvider
from .utils import get_pid_type_from_schema


def inspire_recid_minter(record_uuid, data, do_trigger_all_minters=True):
    """
    Mint Persistent Identifiers for the given record. And optionally trigger
    all other minters.

    Note: this is one of the entry points to mint all (types of) PIDs; the
    other one is the function `mint_pids()`. This is for backward
    compatibility: this function is currently used in many places (eg.
    12 occurrences in inspirehep/config.py).

    Args:
        record_uuid: uuid of the record for which the PID is being created.
        data: record data.
        do_trigger_all_minters: if True, all other minters are triggered.

    Returns: recid PID just created.
    """
    assert '$schema' in data
    args = dict(
        object_type='rec',
        object_uuid=record_uuid,
        pid_type=get_pid_type_from_schema(data['$schema'])
    )
    if 'control_number' in data:
        args['pid_value'] = data['control_number']
    provider = InspireRecordIdProvider.create(**args)
    data['control_number'] = provider.pid.pid_value

    if do_trigger_all_minters:
        minters = MINTERS[:]  # Copy the list in a new var.
        minters.remove(inspire_recid_minter)
        mint_pids(record_uuid, data, minters)

    return provider.pid


def mint_pids(record_uuid, data, minters=None):
    """
    Mint all the PID types for the given record.

    Args:
        record_uuid: uuid of the record for which the PID is being created.
        data: record data.
        minters: collection of callables (the actual minters).

    Returns: all created PIDs.
    """
    if minters is None:
        minters = MINTERS

    for minter in minters:
        minter(record_uuid, data)


@six.add_metaclass(abc.ABCMeta)
class Minter(object):
    def mint(self, record_uuid, data, existent_pids=None):
        """
        Mint a PID for the record with the given uuid and data.

        Args:
            record_uuid: uuid of the record for which the PID is being created.
            data: record data.
            existent_pids: list of existent PIDs already connected to the given
                record.
        """
        # Collect new and existent pid values.
        new_values = self._fetcher(data)
        existent_values = []
        if existent_pids:
            existent_pids = existent_pids.filter_by(pid_type=self.PID_TYPE) \
                .with_entities(PersistentIdentifier.pid_value).all()
            existent_values = [str(x[0]) for x in existent_pids]

        # Compute pids to create and to delete.
        to_delete = set(existent_values) - set(new_values)
        to_create = set(new_values) - set(existent_values)

        # Delete pids.
        for pid_value in to_delete:
            PersistentIdentifier.get(self.PID_TYPE, pid_value).delete()

        # Create pids.
        for pid_value in to_create:
            try:
                PersistentIdentifier.create(
                    pid_type=self.PID_TYPE,
                    pid_value=pid_value,
                    object_type='rec',
                    object_uuid=record_uuid,
                    status=self.STATUS
                )
            except PIDAlreadyExists as exc:
                msg = ('A PID with type %s and value %s already exists and it is' \
                       ' related to another record (current object_uuid = %s)' % (
                       self.PID_TYPE, pid_value, record_uuid))
                current_app.logger.exception(msg)
                raise DuplicatedPIDMinterException(msg)

    def _fetcher(self, data):
        field_values = data.get(self.FIELD_NAME, [])
        return [x['value'] for x in field_values if
                x['schema'].lower() == self.PID_TYPE]


class UrnMinter(Minter):
    FIELD_NAME = 'persistent_identifiers'
    PID_TYPE = 'urn'
    # STATUS = PIDStatus.REGISTERED
    STATUS = PIDStatus.RESERVED


class HdlMinter(Minter):
    FIELD_NAME = 'persistent_identifiers'
    PID_TYPE = 'hdl'
    STATUS = PIDStatus.RESERVED


MINTERS = [
    UrnMinter().mint,
    HdlMinter().mint,
    inspire_recid_minter,
]
