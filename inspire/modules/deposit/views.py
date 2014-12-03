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

from datetime import datetime

from flask import Blueprint, \
    render_template, \
    request, \
    jsonify
from flask.ext.login import login_required
from flask.ext.wtf import Form
from wtforms.fields import DateTimeField, SubmitField

from invenio.base.i18n import _
from invenio.modules.deposit.signals import template_context_created
from invenio.modules.deposit.models import Deposition
from invenio.modules.deposit.views.deposit import blueprint as deposit_blueprint

from utils import process_metadata_for_charts


blueprint = Blueprint(
    'inspire_deposit',
    __name__,
    template_folder='templates',
    static_folder="static",
)


CHART_TYPES = {'column': 'Column',
               'pie': 'Pie'}


class FilterDateForm(Form):

    """Date form."""

    since_date = DateTimeField(
        label=_('From'),
        description='Format: YYYY-MM-DD.')
    until_date = DateTimeField(
        label=_('To'),
        description='Format: YYYY-MM-DD.')
    submit = SubmitField(_("Filter depositions"))


@deposit_blueprint.route('/stats',
                         methods=['GET', 'POST'])
@login_required
def show_stats():
    """Render the stats for all the depositions."""
    form = FilterDateForm()

    submitted_depositions = [d for d in Deposition.get_depositions() if d.has_sip(sealed=True)]

    ctx = process_metadata_for_charts(submitted_depositions)
    ctx.update(dict(
        depositions=submitted_depositions,
        form=form,
        chart_types=CHART_TYPES
    ))

    # Send signal to allow modifications to the template context
    template_context_created.send(
        '%s.%s' % (deposit_blueprint.name, show_stats.__name__),
        context=ctx
    )

    return render_template('deposit/stats/all_depositions.html', **ctx)
