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

"""Theme blueprint in order for template and static files to be loaded."""

from flask import Blueprint, render_template

blueprint = Blueprint(
    'inspirehep_theme',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)


#
# Collections
#

@blueprint.route('/literature', methods=['GET', ])
@blueprint.route('/collection/literature', methods=['GET', ])
@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """View for literature collection landing page."""
    collection = {'name': 'hep'}
    return render_template('inspirehep_theme/search/collection_literature.html',
                           collection=collection)


@blueprint.route('/authors', methods=['GET', ])
@blueprint.route('/collection/authors', methods=['GET', ])
def hepnames():
    """View for authors collection landing page."""
    collection = {'name': 'hepnames'}
    return render_template('inspirehep_theme/search/collection_authors.html',
                           collection=collection)


@blueprint.route('/conferences', methods=['GET', ])
def conferences():
    """View for conferences collection landing page."""
    collection = {'name': 'conferences'}
    return render_template('inspirehep_theme/search/collection_conferences.html',
                           collection=collection)


# @blueprint.route('/jobs', methods=['GET', ])
# def jobs():
#     """View for jobs collection landing page."""
#     return redirect(url_for('search.search', cc='jobs'))


@blueprint.route('/institutions', methods=['GET', ])
def institutions():
    """View for institutions collection landing page."""
    collection = {'name': 'institutions'}
    return render_template('inspirehep_theme/search/collection_institutions.html',
                           collection=collection)


@blueprint.route('/experiments', methods=['GET', ])
def experiments():
    """View for experiments collection landing page."""
    collection = {'name': 'experiments'}
    return render_template('inspirehep_theme/search/collection_experiments.html',
                           collection=collection)


@blueprint.route('/journals', methods=['GET', ])
def journals():
    """View for journals collection landing page."""
    collection = {'name': 'journals'}
    return render_template('inspirehep_theme/search/collection_journals.html',
                           collection=collection)


@blueprint.route('/data', methods=['GET', ])
def data():
    """View for data collection landing page."""
    collection = {'name': 'data'}
    return render_template('inspirehep_theme/search/collection_data.html',
                           collection=collection)


@blueprint.route('/ping')
def ping():
    return 'OK'
