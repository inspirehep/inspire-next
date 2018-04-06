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

from invenio_accounts.models import User

from .base import TestBaseModel


class TestUser(TestBaseModel):
    """
    Create User instances.

    Example:
        >>> from factories.db.invenio_accounts import TestUser
        >>> factory = TestUser.create_from_kwargs(email='foo@bar.com')
        >>> factory.user
        <User (transient 4661300240)>
        >>> factory.user.email
        'foo@bar.com'
    """
    model_class = User

    @classmethod
    def create_from_kwargs(cls, **kwargs):
        instance = cls()
        instance.user = super(TestUser, cls).create_from_kwargs(kwargs)
        return instance
