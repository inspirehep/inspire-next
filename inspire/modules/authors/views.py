# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import

import json
import os
import requests

from flask import abort, \
    Blueprint, \
    jsonify, \
    make_response, \
    render_template, \
    request, \
    url_for, \
    redirect
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb
from werkzeug.datastructures import MultiDict

from flask_login import login_required

from invenio_base.decorators import wash_arguments
from invenio_base.globals import cfg
from invenio_base.i18n import _
from invenio_ext.principal import permission_required
from invenio_workflows.models import BibWorkflowObject

from .acl import viewauthorreview
from .forms import AuthorUpdateForm


blueprint = Blueprint(
    'inspire_authors',
    __name__,
    url_prefix='/author',
    template_folder='templates',
    static_folder="static",
)

default_breadcrumb_root(blueprint, '.')


def convert_for_form(data):
    """Convert jsonalchemy keys to form field names."""
    if "name" in data:
        data["full_name"] = data["name"].get("value")
        try:
            data["given_names"] = data["name"].get("value").split(",")[1].strip()
        except IndexError:
            data["given_names"] = ""
        data["family_name"] = data["name"].get("value").split(",")[0].strip()
        data["display_name"] = data["name"].get("preferred_name")
        data["status"] = data["name"].get("status").lower()
    if "url" in data:
        data["websites"] = []
        for url in data["url"]:
            if "description" not in url:
                data["websites"].append({"webpage": url["url"]})
            else:
                if url["description"].lower() == "twitter":
                    data["twitter_url"] = url["url"]
                elif url["description"].lower() == "blog":
                    data["blog_url"] = url["url"]
                elif url["description"].lower() == "linkedin":
                    data["linkedin_url"] = url["url"]
        del data["url"]
    if "field_categories" in data:
        data["research_field"] = [field["name"].lower() for
                                  field in data["field_categories"]]
    if "positions" in data:
        data["institution_history"] = []
        for position in data["positions"]:
            if not any(
                [
                    key in position for key in ('name', 'rank',
                                                'start_year', 'end_year')
                ]
            ):
                continue
            pos = {}
            pos["name"] = position.get("institution", {}).get("name")
            pos["rank"] = position.get("rank", "")
            pos["start_year"] = position.get("start_date", "")
            pos["end_year"] = position.get("end_date", "")
            pos["current"] = True if position.get("status") else False
            data["institution_history"].append(pos)
            if position.get("email"):
                data["public_email"] = position.get("email")
        data["institution_history"].reverse()
    if "phd_advisors" in data:
        phd_advisors = data["phd_advisors"]
        data["advisors"] = []
        for advisor in phd_advisors:
            adv = {}
            adv["name"] = advisor.get("name", "")
            adv["degree_type"] = advisor.get("degree_type", "")
            data["advisors"].append(adv)
    if "ids" in data:
        for id in data["ids"]:
            try:
                if id["type"] == "ORCID":
                    data["orcid"] = id["value"]
                elif id["type"] == "BAI":
                    data["bai"] = id["value"]
                elif id["type"] == "INSPIRE":
                    data["inspireid"] = id["value"]
            except KeyError:
                # Protect against cases when there is no value in metadata
                pass


@blueprint.route('/validate', methods=['POST'])
def validate():
    """Validate form and return validation errors."""
    if request.method != 'POST':
        abort(400)

    data = request.json or MultiDict({})
    formdata = MultiDict(data or {})

    form = AuthorUpdateForm(formdata=formdata)
    form.validate()

    result = {}
    changed_msgs = dict(
        (name, messages) for name, messages in form.messages.items()
        if name in formdata.keys()
    )
    result['messages'] = changed_msgs

    return jsonify(result)


@blueprint.route('/update', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.update', _('Update author information'))
@login_required
@wash_arguments({'recid': (int, 0)})
def update(recid):
    """View for INSPIRE author update form."""
    from dojson.contrib.marc21.utils import create_record
    from inspire.dojson.hepnames import hepnames

    data = {}
    if recid:
        try:
            url = os.path.join(cfg["AUTHORS_UPDATE_BASE_URL"], "record",
                               str(recid), "export", "xm")
            xml = requests.get(url)
            data = hepnames.do(create_record(xml.content.encode("utf-8")))
            convert_for_form(data)
        except requests.exceptions.RequestException:
            pass
        data["recid"] = recid
    else:
        return redirect(url_for("inspire_authors.new"))
    form = AuthorUpdateForm(data=data)
    ctx = {
        "action": url_for('.submitupdate'),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
    }

    return render_template('authors/forms/update_form.html', form=form, **ctx)


@blueprint.route('/new', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.new', _('New author information'))
@login_required
@wash_arguments({'bai': (unicode, u"")})
def new(bai):
    """View for INSPIRE author new form."""
    data = {}
    if bai:
        # Add BAI information to form in order to keep connection between
        # a HEPName and an author profile.
        data["bai"] = bai

    form = AuthorUpdateForm(data=data)
    ctx = {
        "action": url_for('.submitnew'),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
    }

    return render_template('authors/forms/new_form.html', form=form, **ctx)


@blueprint.route('/newreview', methods=['GET', 'POST'])
@login_required
@permission_required(viewauthorreview.name)
@wash_arguments({'objectid': (int, 0)})
def newreview(objectid):
    """View for INSPIRE author new form review by a cataloger."""
    if not objectid:
        abort(400)
    workflow_object = BibWorkflowObject.query.get(objectid)
    extra_data = workflow_object.get_extra_data()

    form = AuthorUpdateForm(data=extra_data["formdata"], is_review=True)
    ctx = {
        "action": url_for('.reviewaccepted', objectid=objectid),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
        "objectid": objectid
    }

    return render_template('authors/forms/review_form.html', form=form, **ctx)


@blueprint.route('/reviewaccepted', methods=['GET', 'POST'])
@login_required
@permission_required(viewauthorreview.name)
@wash_arguments({'objectid': (int, 0),
                 'approved': (bool, False),
                 'ticket': (bool, False)})
def reviewaccepted(objectid, approved, ticket):
    """Form handler when a cataloger accepts a new author update"""
    if not objectid:
        abort(400)
    workflow_object = BibWorkflowObject.query.get(objectid)
    extra_data = workflow_object.get_extra_data()
    extra_data["approved"] = approved
    extra_data["ticket"] = ticket
    workflow_object.set_extra_data(extra_data)
    workflow_object.save()
    workflow_object.continue_workflow(delayed=True)

    return render_template('authors/forms/new_review_accepted.html',
                           approved=approved)


@blueprint.route('/submitupdate', methods=['POST'])
@login_required
def submitupdate():
    """Form action handler for INSPIRE author update form."""
    from inspire.modules.forms.utils import DataExporter
    from invenio_workflows.models import BibWorkflowObject
    from flask.ext.login import current_user
    form = AuthorUpdateForm(formdata=request.form)
    visitor = DataExporter()
    visitor.visit(form)
    myobj = BibWorkflowObject.create_object(id_user=current_user.get_id())
    myobj.set_data(visitor.data)
    # Start workflow. delayed=True will execute the workflow in the
    # background using, for example, Celery.
    myobj.start_workflow("authorupdate", delayed=True)

    ctx = {
        "inspire_url": get_inspire_url(visitor.data)
    }

    return render_template('authors/forms/update_success.html', **ctx)


@blueprint.route('/submitnew', methods=['POST'])
@login_required
def submitnew():
    """Form action handler for INSPIRE author new form."""
    from inspire.modules.forms.utils import DataExporter
    from invenio_workflows.models import BibWorkflowObject
    from flask.ext.login import current_user
    form = AuthorUpdateForm(formdata=request.form)
    visitor = DataExporter()
    visitor.visit(form)

    myobj = BibWorkflowObject.create_object(id_user=current_user.get_id())
    myobj.set_data(visitor.data)
    # Start workflow. delayed=True will execute the workflow in the
    # background using, for example, Celery.
    myobj.start_workflow("authornew", delayed=True)

    ctx = {
        "inspire_url": get_inspire_url(visitor.data)
    }

    return render_template('authors/forms/new_success.html', **ctx)


@blueprint.route(
    '/<field_name>/',
    methods=['GET', 'POST'])
@login_required
def autocomplete(field_name=None):
    """Auto-complete a form field."""
    term = request.args.get('term')  # value
    limit = request.args.get('limit', 50, type=int)

    form = AuthorUpdateForm()

    result = form.autocomplete(field_name, term, limit=limit)
    result = result if result is not None else []

    # jsonify doesn't return lists as top-level items.
    resp = make_response(
        json.dumps(result, indent=None if request.is_xhr else 2)
    )
    resp.mimetype = "application/json"
    return resp


def get_inspire_url(data):
    """ Generate url for the user to go back to INSPIRE. """
    url = ""
    if "bai" in data and data["bai"]:
        url = "http://inspirehep.net/author/profile/" + data["bai"]
    elif "recid" in data and data["recid"]:
        url = "http://inspirehep.net/record/" + str(data["recid"])
    else:
        url = "http://inspirehep.net/hepnames"
    return url
