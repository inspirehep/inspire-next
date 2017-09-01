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
import re

from celery import shared_task
from flask import current_app

from invenio_db import db


RE_ALPHANUMERIC = re.compile('\W+', re.UNICODE)


@shared_task()
def create_journal_kb_file():
    """Populate refextracts's journal KB from the database.

    Uses two raw DB queries that use syntax specific to PostgreSQL to generate
    a file in the format that refextract expects, that is a list of lines like::

        SOURCE---DESTINATION

    which represents that ``SOURCE`` is translated to ``DESTINATION`` when found.

    Note that refextract expects ``SOURCE`` to be normalized, which means removing
    all non alphanumeric characters, collapsing all contiguous whitespace to one
    space and uppercasing the resulting string.
    """
    refextract_journal_kb_path = current_app.config['REFEXTRACT_JOURNAL_KB_PATH']

    titles_query = db.session.execute("""
        SELECT
            r.json -> 'short_title' AS short_title,
            r.json -> 'journal_title' -> 'title' AS journal_title
        FROM
            records_metadata AS r
        WHERE
            (r.json -> '_collections')::jsonb ? 'Journals'
    """)

    title_variants_query = db.session.execute("""
        SELECT
            r.json -> 'short_title' AS short_title,
            json_array_elements(r.json -> 'title_variants') AS title_variant
        FROM
            records_metadata AS r
        WHERE
            (r.json -> '_collections')::jsonb ? 'Journals'
    """)

    with codecs.open(refextract_journal_kb_path, encoding='utf-8', mode='w') as fd:
        for row in titles_query:
            fd.write(u'{}---{}\n'.format(_normalize(row['short_title']), row['short_title']))
            fd.write(u'{}---{}\n'.format(_normalize(row['journal_title']), row['short_title']))

        for row in title_variants_query:
            fd.write(u'{}---{}\n'.format(_normalize(row['title_variant']), row['short_title']))


def _normalize(s):
    return ' '.join((RE_ALPHANUMERIC.sub(' ', s)).split()).upper()
