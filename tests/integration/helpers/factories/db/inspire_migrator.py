# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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
import os
import pkg_resources
import random
import re

from inspirehep.modules.migrator.models import LegacyRecordsMirror

from .base import TestBaseModel


class TestLegacyRecordsMirror(TestBaseModel):
    """Create Legacy Mirror Record instance."""
    model_class = LegacyRecordsMirror

    re_recid = re.compile('<controlfield.*?tag=.001.*?>(?P<recid>\d+)</controlfield>')

    @classmethod
    def create_from_kwargs(cls, **kwargs):
        instance = cls()

        updated_kwargs = copy.deepcopy(kwargs)

        marcxml = updated_kwargs['_marcxml']

        if 'recid' not in updated_kwargs:
            try:
                updated_kwargs['recid'] = int(cls.re_recid.search(marcxml).group('recid'))
            except AttributeError:
                updated_kwargs['recid'] = random.randint(1, 9) * 5

        instance.legacy_record_mirror = super(TestLegacyRecordsMirror, cls)\
                .create_from_kwargs(updated_kwargs)

        return instance

    @classmethod
    def create_from_file(cls, module_name, filename, **kwargs):
        """Create Legacy Mirror Record instance from file.

        Note:
            It will look inside the ``fixtures`` directory for the given module.

        Example:
            >>> from factories.db.mirror_records import TestLegacyRecordsMirror
            >>> factory = TestLegacyRecordsMirror.create_from_file(__name__, filename)
            >>> factory.legacy_record_mirror
            <LegacyRecordsMirror (transient 4661300240)>
            >>> factory.legacy_record_mirror._marcxml
        """
        path = pkg_resources.resource_filename(
            module_name, os.path.join('fixtures', filename))

        data = open(path).read()
        kwargs['_marcxml'] = data

        return cls.create_from_kwargs(**kwargs)
