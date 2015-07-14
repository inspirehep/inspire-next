# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
    inspire.views
    -------------------------------
"""

import json
from flask import request, Blueprint, render_template, current_app
from flask.ext.menu import register_menu, current_menu
from flask.ext.login import current_user
from invenio.base.i18n import _
from invenio.ext.email import send_email
from invenio.base.globals import cfg


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
    # FIXME Add undo models for each doc type and use them based on
    # collection value
    from inspire.dojson.hep import hep2marc
    from inspire.dojson.utils import legacy_export_as_marc

    return legacy_export_as_marc(hep2marc.do(record))
