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

from flask_mail import Message

from invenio_mail.tasks import send_email


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
    return render_template('inspirehep_theme/search/collection_literature.html',
                           collection='hep')


@blueprint.route('/authors', methods=['GET', ])
@blueprint.route('/collection/authors', methods=['GET', ])
def hepnames():
    """View for authors collection landing page."""
    # collection = {'name': 'hepnames'}
    return render_template('inspirehep_theme/search/collection_authors.html',
                           collection='hepnames')


@blueprint.route('/conferences', methods=['GET', ])
def conferences():
    """View for conferences collection landing page."""
    return render_template('inspirehep_theme/search/collection_conferences.html',
                           collection='conferences')


@blueprint.route('/jobs', methods=['GET', ])
def jobs():
    """View for jobs collection landing page."""
    return redirect(url_for('inspirehep_search.search', cc='jobs'))


@blueprint.route('/institutions', methods=['GET', ])
def institutions():
    """View for institutions collection landing page."""
    return render_template('inspirehep_theme/search/collection_institutions.html',
                           collection='institutions')


@blueprint.route('/experiments', methods=['GET', ])
def experiments():
    """View for experiments collection landing page."""
    return render_template('inspirehep_theme/search/collection_experiments.html',
                           collection='experiments')


@blueprint.route('/journals', methods=['GET', ])
def journals():
    """View for journals collection landing page."""
    return render_template('inspirehep_theme/search/collection_journals.html',
                           collection='journals')


@blueprint.route('/data', methods=['GET', ])
def data():
    """View for data collection landing page."""
    return render_template('inspirehep_theme/search/collection_data.html',
                           collection='data')


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
