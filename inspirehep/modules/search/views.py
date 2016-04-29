# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Search blueprint in order for template and static files to be loaded."""

from __future__ import absolute_import, print_function

import json

from flask import Blueprint, current_app, request, render_template

blueprint = Blueprint('inspirehep_search',
                      __name__,
                      url_prefix='',
                      template_folder='templates',
                      static_folder='static')


@blueprint.route("/search")
def search():
    """Search page ui."""

    #TODO Add rules for the other collections.

    collection = request.values.get('cc', 'hep', type=unicode).lower()
    ctx = {}
    if collection == 'conferences':
        ctx['search_api'] = '/api/conferences/'
        return render_template('search/search_conferences.html', **ctx)
    if collection == 'authors':
        ctx['search_api'] = '/api/authors/'
        return render_template('search/search_authors.html', **ctx)
    if collection == 'data':
        ctx['search_api'] = '/api/data/'
        return render_template('search/search_data.html', **ctx)
    if collection == 'experiments':
        ctx['search_api'] = '/api/experiments/'
        return render_template('search/search_experiments.html', **ctx)
    if collection == 'institutions':
        ctx['search_api'] = '/api/institutions/'
        return render_template('search/search_institutions.html', **ctx)
    if collection == 'journals':
        ctx['search_api'] = '/api/journals/'
        return render_template('search/search_journals.html', **ctx)
    if collection == 'jobs':
        ctx['search_api'] = '/api/jobs/'
        return render_template('search/search_jobs.html', **ctx)

    ctx['search_api'] = current_app.config['SEARCH_UI_SEARCH_API']
    return render_template(current_app.config['SEARCH_UI_SEARCH_TEMPLATE'],
                           **ctx)


def sorted_options(sort_options):
    """Sort sort options for display."""
    return [
        dict(
            title=v['title'],
            value=('-{0}'.format(k)
                   if v.get('default_order', 'asc') == 'desc' else k),
        )
        for k, v in
        sorted(sort_options.items(), key=lambda x: x[1].get('order', 0))
    ]


@blueprint.app_template_filter('format_sortoptions')
def format_sortoptions(sort_options):
    """Create sort options JSON dump for Invenio-Search-JS."""
    return json.dumps(dict(
        options=sorted_options(sort_options)
    ), sort_keys=True)


@blueprint.app_template_filter('default_sortoption')
def default_sortoption(sort_options):
    """Get defualt sort option for Invenio-Search-JS."""
    return sorted_options(sort_options)[0]['value']
