#
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
#

from jinja2.filters import evalcontextfilter
from flask import current_app


@evalcontextfilter
def join_array(eval_ctx, value, separator):

    from jinja2.filters import do_join

    if isinstance(value, basestring):
        value = [value]
    return do_join(eval_ctx, value, separator)


def new_line_after(text):
    if not text:
        return text

    return '%s<br>' % text


def apply_template_on_array(array, template_path, **common_context):
    """
        Renders a template specified by 'template_path'.
        For every item in array, renders the template passing
        the item as 'content' parameter. Additionally ataches
        'common_context' as other rendering arguments.
        Returns list of rendered html strings.
        :param array: iterable with specific context
        :param template_path: path to the template
        :rtype: list of strings
    """

    from collections import Iterable

    rendered = []

    if isinstance(array, basestring):
        array = [array]

    if not isinstance(array, Iterable):
        return rendered

    template = current_app.jinja_env.get_template(template_path)

    for content in array:
        if content:
            rendered.append(template.render(content=content, **common_context))

    return rendered


def get_filters():
    return {
        'join_array': join_array,
        'new_line_after': new_line_after,
        'apply_template_on_array': apply_template_on_array,
    }