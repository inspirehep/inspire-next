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

from invenio_indexer.api import current_record_to_index, RecordIndexer


def create_index_op(record, version_type='external_gte'):
    from inspirehep.modules.records.receivers import enhance_before_index
    index, doc_type = current_record_to_index(record)
    enhance_before_index(record)

    return {
        '_op_type': 'index',
        '_index': index,
        '_type': doc_type,
        '_id': str(record.id),
        '_version': record.revision_id,
        '_version_type': version_type,
        '_source': RecordIndexer._prepare_record(record, index, doc_type),
    }
