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

"""Tools views."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, render_template, request
from wtforms import TextAreaField

from inspirehep.modules.forms.form import INSPIREForm

from .utils import authorlist


blueprint = Blueprint(
    'inspire_tools',
    __name__,
    url_prefix='/tools',
    template_folder='templates',
    static_folder="static",
)


class InputTextForm(INSPIREForm):
    """Input form class."""
    author_string = TextAreaField(
        'Author string', render_kw={'rows': 10, 'cols': 50}
    )


@blueprint.route('/authorlist', methods=['GET', 'POST'])
def authorlist_form():
    """Render the authorlist page for formatting author strings."""
    form = InputTextForm(request.form)
    results = {}
    results_title = ''
    errors = ''
    text = form.author_string.data
    try:
        results = authorlist(text)
        results_title = 'Author list string in MARC21'
    except (AttributeError, ValueError, KeyError) as err:
        errors = err.args
    return render_template(
        'authorlist_form.html',
        results=results,
        title='Format author strings to MARC21',
        form=form,
        results_title=results_title,
        errors=errors,
    )


@blueprint.route('/', methods=['GET'])
def tools_page():
    """Render the splash page for list of tools."""
    return render_template(
        'tools.html',
        title='Tools collection',
    )
