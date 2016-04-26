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
import json

from dateutil.relativedelta import relativedelta
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import current_user

from invenio_mail.tasks import send_email

from flask.ext.menu import current_menu

from inspirehep.modules.records.conference_series import \
    CONFERENCE_CATEGORIES_TO_SERIES
from inspirehep.modules.search.query import perform_query

from invenio_search import current_search_client

from inspirehep.utils.date import datetime
from inspirehep.utils.search import perform_es_search

blueprint = Blueprint('inspirehep_theme', __name__,
                      url_prefix='',
                      template_folder='templates',
                      static_folder='static',
                      )


@blueprint.route('/literature', methods=['GET', ])
@blueprint.route('/collection/literature', methods=['GET', ])
@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """View for literature collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_literature.html',
        collection='hep')


@blueprint.route('/authors', methods=['GET', ])
@blueprint.route('/collection/authors', methods=['GET', ])
def hepnames():
    """View for authors collection landing page."""
    # collection = {'name': 'hepnames'}
    return render_template('inspirehep_theme/search/collection_authors.html',
                           collection='authors')


@blueprint.route('/conferences', methods=['GET', ])
def conferences():
    """View for conferences collection landing page."""

    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')

    six_months_str = (today + relativedelta(months=+6)).strftime('%Y-%m-%d')

    upcoming_conferences = perform_es_search(
        'opening_date:{0}->{1}'.format(today_str, six_months_str),
        1, 100, 'conferences', 'opening_date:asc')

    return render_template(
        'inspirehep_theme/search/collection_conferences.html',
        ctx={'conference_subject_areas': CONFERENCE_CATEGORIES_TO_SERIES,
             'results': upcoming_conferences},
        collection='conferences')


@blueprint.route('/jobs', methods=['GET', ])
def jobs():
    """View for jobs collection landing page."""
    return redirect(url_for('inspirehep_search.search', cc='jobs'))


@blueprint.route('/institutions', methods=['GET', ])
def institutions():
    """View for institutions collection landing page."""
    institutions_list = perform_es_search('', 1, 250, 'institutions')

    return render_template(
        'inspirehep_theme/search/collection_institutions.html',
        ctx={'results': institutions_list}, collection='institutions')


@blueprint.route('/experiments', methods=['GET', ])
def experiments():
    """View for experiments collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_experiments.html',
        collection='experiments')


@blueprint.route('/journals', methods=['GET', ])
def journals():
    """View for journals collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_journals.html',
        collection='journals')


@blueprint.route('/data', methods=['GET', ])
def data():
    """View for data collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_data.html',
        collection='data')


def unauthorized(e):
    """Error handler to show a 401.html page in case of a 401 error."""
    return render_template(current_app.config['THEME_401_TEMPLATE']), 401


def insufficient_permissions(e):
    """Error handler to show a 403.html page in case of a 403 error."""
    return render_template(current_app.config['THEME_403_TEMPLATE']), 403


def page_not_found(e):
    """Error handler to show a 404.html page in case of a 404 error."""
    return render_template(current_app.config['THEME_404_TEMPLATE']), 404


def internal_error(e):
    """Error handler to show a 500.html page in case of a 500 error."""
    return render_template(current_app.config['THEME_500_TEMPLATE']), 500


#
# Ping
#

@blueprint.route('/ping')
def ping():
    return 'OK'


#
# Feedback
#

@blueprint.route('/postfeedback', methods=['POST', ])
def postfeedback():
    """Handler to create a ticket from user feedback."""
    feedback = request.form.get('feedback')
    if feedback == '':
        return jsonify(success=False), 400

    replytoaddr = request.form.get('replytoaddr', None)
    if replytoaddr is None:
        if current_user.is_anonymous:
            return jsonify(success=False), 403
        else:
            replytoaddr = current_user.get('email')
            if replytoaddr == '':
                return jsonify(success=False), 403

    content = 'Feedback:\n{feedback}'.format(feedback=feedback)
    message = {
        'sender': current_app.config['CFG_SITE_SUPPORT_EMAIL'],
        'recipients': [current_app.config['INSPIRELABS_FEEDBACK_EMAIL']],
        'subject': 'INSPIRE Labs Feedback',
        'body': content,
        'reply_to': replytoaddr
    }

    sending = send_email.delay(message)

    if sending.failed():
        return jsonify(success=False), 500
    else:
        return jsonify(success=True)


#
# Menu fixup
#

@blueprint.before_app_first_request
def register_menu_items():
    """Hack to remove children of Settings menu"""

    def menu_fixup():
        current_menu.submenu("settings.change_password").hide()
        current_menu.submenu("settings.groups").hide()
        current_menu.submenu("settings.workflows").hide()
        current_menu.submenu("settings.applications").hide()
        current_menu.submenu("settings.oauthclient").hide()

    current_app.before_first_request_funcs.append(menu_fixup)
