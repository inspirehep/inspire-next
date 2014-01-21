#
## This file is part of Invenio.
## Copyright (C) 2014 INSPIRE.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

from invenio.ext.template.context_processor import \
    register_template_context_processor

from flask import session, request


def setup_app(app):
    from invenio.modules.records.views import blueprint as records_blueprint
    from invenio.modules.search.forms import EasySearchForm

    @records_blueprint.before_request
    def register_add_searchform():

        @register_template_context_processor
        def add_searchform():
            return {
                'easy_search_form': EasySearchForm(csrf_enabled=False),
                'searchbar_enable': True
            }

    from invenio.modules.search.views.search import blueprint as search_blueprint

    @search_blueprint.before_request
    def register_capture_search_params():

        @register_template_context_processor
        def capture_search_params():
            session["LAST_SEARCH_PARAMS"] = request.args.copy()
            collection = request.args.get('cc')
            if collection:
                session['COLLECTION'] = collection
            return {}