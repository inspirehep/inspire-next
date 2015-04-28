#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

from flask import Blueprint, render_template, url_for, request, abort
from werkzeug.datastructures import MultiDict

from inspire.modules.forms import fields

from invenio.base.i18n import _

from wtforms.validators import DataRequired

from .form import InspireForm


blueprint = Blueprint(
    'inspire_forms',
    __name__,
    url_prefix='/forms',
    template_folder='templates',
    static_folder="static",
)


class DemoForm(InspireForm):

    """Demo sample Form."""

    nickname = fields.StringField(
        _("Nickname"),
        validators=[DataRequired(message=_("Nickname not provided"))],
        placeholder="My placeholder",
        description="My description",
        export_key="custom_nickname_key"
        )
    password = fields.PasswordField(_("Password"))
    referer = fields.HiddenField()
    login_method = fields.HiddenField()

    _title = _("Demo INSPIRE form")

    groups = [
        ('Personal information',
            ['nickname', 'password']),
    ]


@blueprint.route('/demoform', methods=['GET', 'POST'])
def demoform():
    """View for INSPIRE demo form."""
    # from inspire.modules.forms.utils import DataExporter

    form = DemoForm(data={"nickname": "John Doe"})
    ctx = {
        "action": url_for('.demoform'),
        "name": "inspireForm",
        "id": "inspireForm",
    }
    if form.validate_on_submit():
        # If it is needed to post process the form keys, for example to match
        # the names in the JSONAlchemy, one can use the DataExporter.
        # The keys will then be renamed using `export_key` parameter.
        # visitor = DataExporter()
        # visitor.visit(form)
        # visitor.data
        from invenio.modules.workflows.models import BibWorkflowObject
        from flask.ext.login import current_user
        myobj = BibWorkflowObject.create_object(id_user=current_user.get_id())
        myobj.set_data(form.data)
        # Start workflow. delayed=True will execute the workflow in the
        # background using, for example, Celery.
        myobj.start_workflow("demoworkflow", delayed=True)
        return render_template('forms/form_demo_success.html', form=form)
    return render_template('forms/form_demo.html', form=form, **ctx)
