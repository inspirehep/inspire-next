# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""INSPIRE authors blueprint."""

from __future__ import absolute_import, print_function

import os
import re
import requests

from flask_babelex import gettext as _

from flask import abort, \
    Blueprint, \
    current_app, \
    jsonify, \
    render_template, \
    request, \
    url_for, \
    redirect
from flask_breadcrumbs import register_breadcrumb
from werkzeug.datastructures import MultiDict

from flask_login import login_required

from inspirehep.dojson.utils import strip_empty_values

# from invenio_ext.principal import permission_required
# from invenio_workflows.models import BibWorkflowObject

# from .acl import viewauthorreview
from .forms import AuthorUpdateForm


blueprint = Blueprint('inspirehep_authors',
                      __name__,
                      url_prefix='/author',
                      template_folder='templates',
                      static_folder='static')


def convert_for_form(data):
    """
    Convert author data model form field names.

    FIXME This might be better in a different file and as a dojson conversion
    """
    if "name" in data:
        data["full_name"] = data["name"].get("value")
        try:
            data["given_names"] = data["name"].get(
                "value").split(",")[1].strip()
        except IndexError:
            data["given_names"] = ""
        data["family_name"] = data["name"].get("value").split(",")[0].strip()
        data["display_name"] = data["name"].get("preferred_name")
        data["status"] = data["name"].get("status", "").lower()
    if "urls" in data:
        data["websites"] = []
        for url in data["urls"]:
            if "description" not in url:
                data["websites"].append({"webpage": url["value"]})
            else:
                if url["description"].lower() == "twitter":
                    data["twitter_url"] = url["value"]
                elif url["description"].lower() == "blog":
                    data["blog_url"] = url["value"]
                elif url["description"].lower() == "linkedin":
                    data["linkedin_url"] = url["value"]
        del data["urls"]
    if "field_categories" in data:
        data["research_field"] = data['field_categories']
    if "positions" in data:
        data["institution_history"] = []
        for position in data["positions"]:
            if not any(
                [
                    key in position for key in ('name', 'rank',
                                                'start_year', 'end_year')
                ]
            ):
                if 'email' in position:
                    # Only email available, take as public_email
                    data["public_email"] = position.get("email")
                continue
            pos = {}
            pos["name"] = position.get("institution", {}).get("name")
            pos["rank"] = position.get("rank", "")
            pos["start_year"] = position.get("start_date", "")
            pos["end_year"] = position.get("end_date", "")
            pos["current"] = True if position.get("status") else False
            pos["old_email"] = position.get("old_email", "")
            if position.get("email"):
                pos["email"] = position.get("email", "")
                if not data.get("public_email"):
                    data["public_email"] = position.get("email")
            data["institution_history"].append(pos)
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


@blueprint.route('/validate', methods=['POST'])
def validate():
    """Validate form and return validation errors.

    FIXME: move to forms module as a generic /validate where we can pass
    the for class to validate.
    """
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
def update():
    """View for INSPIRE author update form."""
    from dojson.contrib.marc21.utils import create_record
    from inspirehep.dojson.hepnames import hepnames

    recid = request.values.get('recid', 0, type=int)

    data = {}
    if recid:
        try:
            url = os.path.join(current_app.config["AUTHORS_UPDATE_BASE_URL"], "record",
                               str(recid), "export", "xm")
            xml = requests.get(url)
            record_regex = re.compile(
                r"\<record\>.*\<\/record\>", re.MULTILINE + re.DOTALL)
            xml_content = record_regex.search(xml.content).group()

            data = strip_empty_values(
                hepnames.do(create_record(xml_content)))  # .encode("utf-8")
            convert_for_form(data)
        except requests.exceptions.RequestException:
            pass
        data["recid"] = recid
    else:
        return redirect(url_for("inspirehep_authors.new"))
    form = AuthorUpdateForm(data=data)
    ctx = {
        "action": url_for('.submitupdate'),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
    }

    # FIXME create template in authors module
    return render_template('authors/forms/update_form.html', form=form, **ctx)


@blueprint.route('/submitupdate', methods=['POST'])
@login_required
def submitupdate():
    """Form action handler for INSPIRE author update form."""
    from inspirehep.modules.forms.form import DataExporter
    from invenio_workflows.models import BibWorkflowObject
    from flask_login import current_user
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
