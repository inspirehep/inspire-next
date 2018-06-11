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

from __future__ import absolute_import, division, print_function

import copy
import random
import uuid

from invenio_pidstore.models import PIDStatus, PersistentIdentifier

from .base import TestBaseModel


class TestPersistentIdentifier(TestBaseModel):
    """Create a PersistentIdentifier instance.

    Example:
        >>> from factories.db.invenio_persistent_identifier import TestPersistentIdentifier
        >>> factory = TestPersistentIdentifier.create_from_kwargs(object_uuid='1111-1111-1111-1111')
        >>> factory.persistent_indentifier
        <PersistentIdentifier (transient 4661300240)>
        >>> factory.persistent_identifier
    """
    model_class = PersistentIdentifier

    @classmethod
    def create_from_kwargs(cls, **kwargs):
        instance = cls()

        updated_kwargs = copy.deepcopy(kwargs)
        if not kwargs.pop('pid_value', None):
            updated_kwargs['pid_value'] = random.randint(1, 9) * 5
        if not kwargs.pop('pid_type', None):
            updated_kwargs['pid_type'] = 'lit'
        if not kwargs.pop('object_type', None):
            updated_kwargs['object_type'] = 'rec'
        if not kwargs.pop('object_uuid', None):
            updated_kwargs['object_uuid'] = uuid.uuid4()
        if not kwargs.pop('status', None):
            updated_kwargs['status'] = PIDStatus.REGISTERED

        instance.persistent_identifier = super(
            TestPersistentIdentifier, cls).create_from_kwargs(updated_kwargs)

        return instance
