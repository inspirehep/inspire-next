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

"""INSPIRE authors views."""

from __future__ import absolute_import, division, print_function

from flask import (
    abort,
    Blueprint,
    redirect,
)
from flask_login import login_required

from .permissions import holdingpen_author_permission

blueprint = Blueprint(
    'inspirehep_authors',
    __name__,
    url_prefix='/authors',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/validate', methods=['POST'])
def validate():
    """Validate form and return validation errors.

    FIXME: move to forms module as a generic /validate where we can pass
    the for class to validate.
    """
    abort(400)


@blueprint.route('/new', methods=['GET'])
def new():
    """Deprecated View for INSPIRE author new form."""
    return redirect('/submissions/authors', 301)


@blueprint.route('/<int:recid>/update', methods=['GET'])
def update(recid):
    """Deprecated View for INSPIRE author update form."""
    return redirect('/submissions/authors/{}'.format(recid), 301)


@blueprint.route('/update/submit', methods=['POST'])
def submitupdate():
    """Deprecated Form action handler for INSPIRE author update form."""
    return redirect('/submissions/authors', 301)


@blueprint.route('/new/submit', methods=['POST'])
def submitnew():
    """Deprecated Form action handler for INSPIRE author new form."""
    return redirect('/submissions/authors', 301)


@blueprint.route('/new/review', methods=['GET'])
@login_required
@holdingpen_author_permission.require(http_exception=403)
def newreview():
    """Deprecated View for INSPIRE author new form review by a cataloger."""
    return redirect('/submissions/authors', 301)


@blueprint.route('/new/review/submit', methods=['POST'])
@login_required
@holdingpen_author_permission.require(http_exception=403)
def reviewhandler():
    """Deprecated Form handler when a cataloger accepts an author review."""
    return redirect('/submissions/authors', 301)


@blueprint.route('/holdingpenreview', methods=['GET', 'POST'])
@login_required
@holdingpen_author_permission.require(http_exception=403)
def holdingpenreview():
    """Deprecated Handler for approval or rejection of new authors in Holding Pen."""
    return redirect('/submissions/authors', 301)
