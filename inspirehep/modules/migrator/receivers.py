# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio_base import signals
from invenio_base.scripts.database import create, recreate, drop


def create_indices(sender, **kwargs):
    """Create record and Holding Pen indices."""
    from .manage import create_indices
    create_indices()


def delete_indices(sender, **kwargs):
    """Delete record and Holding Pen indices."""
    from .manage import delete_indices
    delete_indices()


signals.pre_command.connect(delete_indices, sender=drop)
signals.pre_command.connect(create_indices, sender=create)
signals.pre_command.connect(delete_indices, sender=recreate)
signals.pre_command.connect(create_indices, sender=recreate)
