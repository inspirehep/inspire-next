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

import contextlib

from celery import shared_task
import codecs
from flask import current_app

from invenio_db import db


@contextlib.contextmanager
def file_open_for_editing(fpath):
    fh = codecs.open(fpath, encoding='utf-8', mode='w')

    yield fh

    fh.close()


@shared_task()
def create_journal_kb_file():
    querystring = "SELECT short_titles, title_variants " \
                  "FROM records_metadata as r, " \
                  "json_array_elements(r.json -> 'short_titles') as short_titles, " \
                  "json_array_elements(r.json -> 'title_variants') as title_variants"

    results = db.session.execute(querystring)

    if results.rowcount > 1:
        with file_open_for_editing(current_app.config['REFEXTRACT_JOURNAL_KB_PATH']) as fh:

            for row in results:
                alt_title = row['title_variants'].get('title')
                short_title = row['short_titles'].get('title')
                fh.write(u'{}---{}'.format(alt_title, short_title))
                fh.write('\n')
