#
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
#

from flask import Blueprint, \
    request, \
    jsonify
from flask.ext.login import login_required

from invenio.modules.deposit.views.deposit import blueprint as deposit_blueprint

blueprint = Blueprint(
    'inspire_deposit',
    __name__,
    template_folder='templates',
    static_folder="static",
)


@deposit_blueprint.route('/<depositions:deposition_type>/split_publication/',
                         methods=['GET'])
@login_required
def split_publication_note(deposition_type):
    """Journal reference extraction JSON API."""
    result = {}
    journal_ref = request.args.get('journal-ref', None)

    if journal_ref:
        from invenio.legacy.refextract.api import extract_journal_reference
        references = extract_journal_reference(journal_ref)
        if references:
            for r in references:
                result['journal_{0}'.format(r)] = references[r]

    return jsonify(result)
