# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Editor api views."""

from __future__ import absolute_import, division, print_function

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user
from fs.opener import fsopendir
from werkzeug.utils import secure_filename

from inspirehep.modules.editor.permissions import (
    editor_permission,
    editor_use_api_permission,
)
from inspirehep.modules.tools import authorlist

from inspirehep.utils.url import copy_file
from inspirehep.modules.workflows.workflows.manual_merge import start_merger

MAX_UNIQUE_KEY_COUNT = 100

blueprint_api = Blueprint(
    'inspirehep_editor',
    __name__,
    url_prefix='/editor',
)


@blueprint_api.route('/<endpoint>/<pid_value>/permission', methods=['GET'])
@editor_permission
def check_permission(endpoint, pid_value):
    """Check if logged in user has permission to open the given record.

    Used by record-editor on startup.
    """
    return jsonify(success=True)


@blueprint_api.route('/authorlist/text', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def authorlist_text():
    """Run authorlist on a piece of text."""
    try:
        parsed_authors = authorlist(request.json['text'])
        return jsonify(parsed_authors)
    except Exception as err:
        return jsonify(status=500, message=u' / '.join(err.args)), 500


@blueprint_api.route('/manual_merge', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def manual_merge():
    """Start a manual merge workflow on two records.

    Todo:
        The following two assertions must be replaced with proper access
        control checks, as currently any curator who has access to the
        editor API can merge any two records, even if they are not among
        those who can see or edit them.

    """
    assert request.json['head_recid']
    assert request.json['update_recid']

    workflow_object_id = start_merger(
        request.json['head_recid'],
        request.json['update_recid'],
        current_user.get_id(),
    )

    return jsonify(workflow_object_id=workflow_object_id)


@blueprint_api.route('/upload', methods=['POST'])
@editor_use_api_permission.require(http_exception=403)
def upload_files():
    if 'file' not in request.files:
        return jsonify(success=False, message='No file part'), 400

    attachment = request.files['file']
    if not attachment:
        return

    filedir = current_app.config['RECORD_EDITOR_FILE_UPLOAD_FOLDER']
    fs = fsopendir(filedir, create_dir=True)
    filename = secure_filename(attachment.filename)
    base_filename = filename
    count = 1
    while fs.isfile(filename) and count < MAX_UNIQUE_KEY_COUNT:
        filename = '%s_%s' % (base_filename, count)
        count += 1

    with fs.open(filename, mode='wb') as remote_file:
        copy_file(attachment.stream, remote_file)

    full_url = fs.getpathurl(filename, allow_none=True)
    if not full_url:
        full_url = fs.getsyspath(filename)

    return jsonify({'path': full_url})
