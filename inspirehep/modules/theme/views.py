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

"""Theme views."""

from __future__ import absolute_import, division, print_function

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
)


blueprint = Blueprint(
    'inspirehep_theme',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/', methods=['GET', ])
def index():
    return render_template('inspirehep_theme/inspire_labs_cover.html')

#
# Error handlers
#


def unauthorized(error):
    return render_template(current_app.config['THEME_401_TEMPLATE']), 401


def insufficient_permissions(error):
    return render_template(current_app.config['THEME_403_TEMPLATE']), 403


def page_not_found(error):
    return render_template(current_app.config['THEME_404_TEMPLATE']), 404


def internal_error(error):
    return render_template(current_app.config['THEME_500_TEMPLATE']), 500

#
# Legacy redirects
#


@blueprint.route('/record/<control_number>')
def record(control_number):
    try:
        pid = PersistentIdentifier.query.filter_by(
            pid_value=control_number).one()
    except NoResultFound:
        abort(404)

    return redirect('/{endpoint}/{control_number}'.format(
        endpoint=get_endpoint_from_pid_type(pid.pid_type),
        control_number=control_number)), 301


@blueprint.route('/author/new')
def author_new():
    bai = request.values.get('bai', None, type=str)
    return redirect(url_for('inspirehep_authors.new', bai=bai)), 301


@blueprint.route('/author/update')
def author_update():
    recid = request.values.get('recid', None, type=str)
    if recid:
        return redirect(
            url_for('inspirehep_authors.update', recid=recid)
        ), 301
    else:
        return redirect(url_for('inspirehep_authors.new')), 301


@blueprint.route('/submit/literature/create')
def literature_new():
    return redirect(url_for('inspirehep_literature_suggest.create')), 301


#
# Redirect on login with ORCID
#

@blueprint.route('/account/settings/linkedaccounts/', methods=['GET'])
def linkedaccounts():
    """Redirect to the homepage when logging in with ORCID."""
    return redirect('/')


@blueprint.route('/login_success', methods=['GET'])
def login_success():
    """Injects current user to the template and passes it to the parent tab."""
    return render_template(
        'inspirehep_theme/login_success.html',
        user={
            'data': {
                'email': current_user.email,
                'roles': [role.name for role in current_user.roles]
            }
        }
    )
