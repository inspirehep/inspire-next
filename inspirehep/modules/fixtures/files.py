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

"""Functions for searching ES and returning the results."""

from __future__ import absolute_import, division, print_function

import os

from flask import current_app

from invenio_db import db

from invenio_files_rest.models import Location


def init_default_storage_path():
    """Init default file store location."""
    try:
        uri = current_app.config['BASE_FILES_LOCATION']
        if uri.startswith('/') and not os.path.exists(uri):
            os.makedirs(uri)
        loc = Location(
            name="default",
            uri=uri,
            default=True
        )
        db.session.add(loc)
        db.session.commit()
        return loc
    except Exception:
        db.session.rollback()
        raise


def init_workflows_storage_path(default=False):
    """Init workflows file store location."""
    try:
        uri = current_app.config['WORKFLOWS_FILE_LOCATION']
        if uri.startswith('/') and not os.path.exists(uri):
            os.makedirs(uri)
        loc = Location(
            name=current_app.config["WORKFLOWS_DEFAULT_FILE_LOCATION_NAME"],
            uri=uri,
            default=False
        )
        db.session.add(loc)
        db.session.commit()
        return loc
    except Exception:
        db.session.rollback()
        raise


def init_records_files_storage_path(default=False):
    """Init records file store location."""
    try:
        uri = os.path.join(
            current_app.config['BASE_FILES_LOCATION'],
            "records", "files"
        )
        if uri.startswith('/') and not os.path.exists(uri):
            os.makedirs(uri)
        loc = Location(
            name=current_app.config["RECORDS_DEFAULT_FILE_LOCATION_NAME"],
            uri=uri,
            default=False
        )
        db.session.add(loc)
        db.session.commit()
        return loc
    except Exception:
        db.session.rollback()
        raise


def init_all_storage_paths():
    """Init all storage paths."""
    init_default_storage_path()
    init_workflows_storage_path()
    init_records_files_storage_path()
