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

from flask import (
    Blueprint,
    jsonify,
)
from flask.views import MethodView

from sqlalchemy import desc
from sqlalchemy.sql.expression import false

from inspirehep.modules.migrator.permissions import migrator_use_api_permission

from .dumper import migrator_error_list_dumper
from .models import LegacyRecordsMirror


blueprint = Blueprint(
    'inspire_migrator',
    __name__,
    url_prefix='/migrator',
)


class MigratorErrorListResource(MethodView):
    """Return a list of errors belonging to invalid mirror records."""
    decorators = [migrator_use_api_permission.require(http_exception=403)]

    def get(self):
        errors = LegacyRecordsMirror.query\
            .filter(LegacyRecordsMirror.valid == false())\
            .filter(LegacyRecordsMirror.collection != 'DELETED')\
            .order_by(desc(LegacyRecordsMirror.last_updated)).all()

        data = {'data': errors}
        response = jsonify(migrator_error_list_dumper(data))

        return response, 200


migrator_error_list_resource = MigratorErrorListResource.as_view(
    'migrator_error_list_resource')
blueprint.add_url_rule(
    '/errors',
    view_func=migrator_error_list_resource,
)
