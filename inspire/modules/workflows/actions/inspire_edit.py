# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from wtforms import TextField, Form, SubmitField, BooleanField
from flask import render_template


def bootstrap_submit(field):
    """
    Submit button for edit record action
    """
    html = u'<input %s >' \
           % html_params(id="submitButton",
                         class_="btn btn-sm btn-primary",
                         name="submitButton",
                         type="submit",)
    return HTMLString(u''.join(html))


class edit_record(Form):
    recid = TextField(label='Rec ID')
    core = BooleanField(label='Core')
    field_code = TextField(label='Field Code')
    type_code = TextField(label='Type Code')
    submit = SubmitField(label="Submit", widget=bootstrap_submit)

    def render(self, *args, **kwargs):
        return render_template('workflows/hp_edit_record_widget.html')

    def run(self):
        pass


edit_record.name = 'Edit Record'
