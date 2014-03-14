# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

from flask import Blueprint, render_template
from flask.ext.menu import register_menu
from invenio.base.i18n import _
# from flask.ext.breadcrumbs import register_breadcrumb

blueprint = Blueprint('inspire', __name__, url_prefix="",
                      template_folder='templates', static_folder='static')


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
