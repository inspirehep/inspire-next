# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Inspire views."""

import json

from flask import request, Blueprint, render_template, current_app
from flask.ext.menu import register_menu, current_menu
from flask.ext.login import current_user

from invenio_base.i18n import _
from invenio_ext.email import send_email
from invenio_base.globals import cfg


blueprint = Blueprint('inspire', __name__, url_prefix="",
                      template_folder='templates', static_folder='static')


@blueprint.before_app_first_request
def register_menu_items():
    """Hack to remove children of Settings menu"""
    def menu_fixup():
        item = current_menu.submenu("settings.groups")
        item.hide()
        item = current_menu.submenu("settings.workflows")
        item.hide()
        item = current_menu.submenu("settings.applications")
        item.hide()
        item = current_menu.submenu("settings.oauthclient")
        item.hide()
    current_app.before_first_request_funcs.append(menu_fixup)


#
# Static pages
#

@blueprint.route('/about', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.about', _('About'), order=1)
# @register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def about():
    return render_template('inspire/about.html')


@blueprint.route('/privacy', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.privacy', _('Privacy'), order=2)
# @register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def privacy():
    return render_template('inspire/privacy.html')


@blueprint.route('/faq', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.faq', _('FAQ'), order=3)
# @register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def faq():
    return render_template('inspire/faq.html')


#
# Collections
#

@blueprint.route('/literature', methods=['GET', ])
@blueprint.route('/collection/literature', methods=['GET', ])
def hep():
    """View for literature collection landing page."""
    return render_template('search/collection_literature.html',
                           collection_name='literature')


@blueprint.route('/authors', methods=['GET', ])
@blueprint.route('/collection/authors', methods=['GET', ])
def hepnames():
    """View for authors collection landing page."""
    return render_template('search/collection_authors.html',
                           collection_name='authors')


@blueprint.route('/conferences', methods=['GET', ])
def conferences():
    """View for conferences collection landing page."""
    return render_template('search/collection_conferences.html',
                           collection_name='conferences')


@blueprint.route('/jobs', methods=['GET', ])
def jobs():
    """View for jobs collection landing page."""
    return render_template('search/collection_jobs.html',
                           collection_name='jobs')


@blueprint.route('/institutions', methods=['GET', ])
def institutions():
    """View for institutions collection landing page."""
    return render_template('search/collection_institutions.html',
                           collection_name='institutions')


@blueprint.route('/experiments', methods=['GET', ])
def experiments():
    """View for experiments collection landing page."""
    return render_template('search/collection_experiments.html',
                           collection_name='experiments')


@blueprint.route('/journals', methods=['GET', ])
def journals():
    """View for journals collection landing page."""
    return render_template('search/collection_journals.html',
                           collection_name='journals')


@blueprint.route('/data', methods=['GET', ])
def data():
    """View for data collection landing page."""
    return render_template('search/collection_data.html',
                           collection_name='data')


#
# Feedback handler
#

@blueprint.route('/postfeedback', methods=['POST', ])
def postfeedback():
    """Handler to create a ticket for user feedback."""
    subject = "INSPIRE Labs feedback"

    feedback = json.loads(request.form.get("data"))

    content = """
Feedback:

{feedback}
    """.format(feedback=feedback)

    # fd, temp_path = mkstemp(suffix=".png")
    # fh = os.fdopen(fd, "wb")
    # fh.write("".join(feedback_data[1].split(",")[1:]).decode('base64'))
    # fh.close()

    # attachments = [temp_path]
    attachments = []

    if send_email(fromaddr=cfg['CFG_SITE_SUPPORT_EMAIL'],
                  toaddr=cfg['INSPIRELABS_FEEDBACK_EMAIL'],
                  subject=subject,
                  content=content,
                  replytoaddr=current_user.get("email"),
                  attachments=attachments):
        return json.dumps(
            {'success': True}
        ), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps(
            {'success': False}
        ), 500, {'ContentType': 'application/json'}

#
# Jinja2 filters
#


@blueprint.app_template_filter('marcxml')
def marcxml_filter(record):
    from inspire.dojson.hep import hep2marc
    from inspire.dojson.hepnames import hepnames2marc
    from inspire.dojson.utils import legacy_export_as_marc

    collections = [
        collection['primary'] for collection in record["collections"]
    ]

    if "HEP" in collections:
        return legacy_export_as_marc(hep2marc.do(record))
    elif "HEPNAMES" in collections:
        return legacy_export_as_marc(hepnames2marc.do(record))
