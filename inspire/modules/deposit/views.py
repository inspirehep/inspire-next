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
    jsonify, \
    abort
from flask.ext.login import login_required

from invenio.modules.deposit.models import Deposition, DepositionType
from invenio.modules.deposit.views.deposit import blueprint as deposit_blueprint

from utils import process_metadata_for_charts
from forms import FilterDateForm


blueprint = Blueprint(
    'inspire_deposit',
    __name__,
    template_folder='templates',
    static_folder="static",
)


CHART_TYPES = {'column': 'Column',
               'pie': 'Pie'}


@deposit_blueprint.route('/<depositions:deposition_type>/stats',
                         methods=['GET'])
@login_required
def show_stats(deposition_type):
    """Render the stats for all the depositions."""
    if len(DepositionType.keys()) <= 1 and \
       DepositionType.get_default() is not None:
        abort(404)

    form = FilterDateForm()

    deptype = DepositionType.get(deposition_type)
    submitted_depositions = [d for d in Deposition.get_depositions(type=deptype) if d.has_sip(sealed=True)]

    ctx = process_metadata_for_charts(submitted_depositions)
    ctx.update(dict(
        deposition_type=deptype,
        depositions=submitted_depositions,
        form=form,
        chart_types=CHART_TYPES
    ))

    return render_template('deposit/stats/all_depositions.html', **ctx)


@deposit_blueprint.route('/<depositions:deposition_type>/stats/api',
                         methods=['GET'])
@login_required
def stats_api(deposition_type):
    """Get stats JSON."""
    deptype = DepositionType.get(deposition_type)
    submitted_depositions = [d for d in Deposition.get_depositions(type=deptype) if d.has_sip(sealed=True)]

    if request.args.get('since_date') is not None:
        since_date = datetime.strptime(request.args['since_date'],
                                       "%Y-%m-%d").replace(hour=0, minute=0)
        submitted_depositions = [d for d in submitted_depositions if d.created >= since_date]

    if request.args.get('until_date') is not None:
        until_date = datetime.strptime(request.args['until_date'],
                                       "%Y-%m-%d").replace(hour=23, minute=59)
        submitted_depositions = [d for d in submitted_depositions if d.created <= until_date]

    result = process_metadata_for_charts(submitted_depositions,
                                         bool(request.args.get('include_hidden', None)))

    resp = jsonify(result)

    return resp
