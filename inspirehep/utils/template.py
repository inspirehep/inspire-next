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

"""Utils related to Jinja templates."""

from __future__ import absolute_import, division, print_function

from flask import current_app


def render_macro_from_template(name, template, app=None, ctx=None):
    """Render macro with the given context.

    :param name: macro name.
    :type name: string.
    :param template: template name.
    :type template: string.
    :param app: Flask app.
    :type app: object.
    :param ctx: parameters of the macro.
    :type ctx: dict.
    :return: unicode string with rendered macro.
    """
    ctx = ctx or {}
    app = app or current_app
    tpl = app.jinja_env.get_template(template)
    macro = getattr(tpl.make_module(), name)
    return unicode(macro(**ctx))
