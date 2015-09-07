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

"""Function for sending robotuploads to other Invenio instances."""

import six
import StringIO

from werkzeug.utils import import_string


def get_json_from_marcxml(marcxml):
    from invenio.base.globals import cfg
    source = StringIO.StringIO(marcxml)

    processor = cfg["RECORD_PROCESSORS"]["marcxml"]
    if isinstance(processor, six.string_types):
        processor = import_string(processor)

    records = list(processor(source))
    source.close()
    return records
