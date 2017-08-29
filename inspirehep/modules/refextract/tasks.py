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

"""Refextract tasks."""

from __future__ import absolute_import, division, print_function

import codecs
import contextlib

from celery import shared_task
from flask import current_app

from invenio_db import db


@contextlib.contextmanager
def file_open_for_editing(path):
    fd = codecs.open(path, encoding='utf-8', mode='w')

    yield fd

    fd.close()


@shared_task()
def create_journal_kb_file():
    result = db.session.execute("""
        SELECT
            r.json -> 'short_title' AS short_title,
            json_array_elements(r.json -> 'title_variants') AS title_variants
        FROM
            records_metadata AS r
        WHERE
            (r.json -> 'short_title') IS NOT NULL;
    """)

    with file_open_for_editing(current_app.config['REFEXTRACT_JOURNAL_KB_PATH']) as fd:
        for row in result:
            fd.write(u'{}---{}\n'.format(row['title_variants'], row['short_title']))
