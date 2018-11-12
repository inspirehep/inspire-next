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

from flask_security.utils import login_user, verify_password
from flask import Blueprint, jsonify, request

from invenio_accounts.models import User


login_blueprint = Blueprint(
    'inspirehep_accounts_login',
    __name__,
)


@login_blueprint.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    email = body['email']
    password = body['password']
    user = User.query.filter_by(email=email).one_or_none()
    if user and verify_password(password, user.password):
        login_user(user)
        return jsonify({
            'data': {
                'email': user.email,
                'roles': [role.name for role in user.roles]
            }
        })
    return jsonify({
        'message': 'Email or password is incorrect'
    }), 422
