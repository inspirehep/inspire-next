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

from flask import session, request
from invenio.ext.template.context_processor import \
    register_template_context_processor


def setup_app(app):
    from invenio_records.views import blueprint as records_blueprint
    from invenio.modules.deposit.views.deposit import blueprint \
        as deposit_blueprint

    records_blueprint.before_request(register_add_searchform)
    deposit_blueprint.before_request(register_add_searchform)

    from invenio.modules.search.views.search import blueprint as search_blueprint

    @search_blueprint.before_request
    def register_capture_search_params():

        @register_template_context_processor
        def capture_search_params():
            session["inspire-last-search-params"] = request.args.copy()
            collection = request.args.get('cc')
            if collection:
                session['inspire-current-collection'] = collection
            return {}

def register_add_searchform():

    @register_template_context_processor
    def add_searchform():
        from invenio.modules.search.forms import EasySearchForm
        from invenio.modules.collections.models import Collection
        return {
            'easy_search_form': EasySearchForm(csrf_enabled=False),
            'searchbar_enable': True,
            'collection': Collection.query.get_or_404(1)
        }
