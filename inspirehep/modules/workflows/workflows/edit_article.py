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

from inspirehep.modules.workflows.tasks.actions import validate_record
from inspirehep.modules.workflows.tasks.submission import send_robotupload
from inspirehep.modules.workflows.utils import get_resolve_edit_article_callback_url
from inspirehep.utils.record_getter import get_db_record
from ..utils import with_debug_logging


@with_debug_logging
def change_status_to_waiting(obj, eng):
    obj.extra_data['callback_url'] = get_resolve_edit_article_callback_url()
    eng.wait(msg='Waiting for curation.')


def update_record(obj, eng):
    control_number = obj.data['control_number']
    record = get_db_record('lit', control_number)
    record.update(obj.data)
    record.commit()


class EditArticle(object):
    """Editing workflow for Literature collection."""

    name = 'edit_article'
    data_type = 'hep'

    workflow = (
        [
            change_status_to_waiting,
            validate_record('hep'),
            send_robotupload(mode='replace'),
            update_record,
        ]
    )
