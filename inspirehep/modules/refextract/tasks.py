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

from celery import shared_task
from flask import current_app

from invenio_db import db

from inspirehep.modules.refextract.utils import KbWriter


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
            jsonb_array_elements((r.json -> 'title_variants')::jsonb) AS title_variant
        FROM
            records_metadata AS r
        WHERE
            (r.json -> '_collections')::jsonb ? 'Journals'
    """)

    with KbWriter(kb_path=refextract_journal_kb_path) as kb_fd:
        for row in titles_query:
            kb_fd.add_entry(
                value=row['short_title'],
                kb_key=row['short_title'],
            )
            kb_fd.add_entry(
                value=row['journal_title'],
                kb_key=row['short_title'],
            )

        for row in title_variants_query:
            kb_fd.add_entry(
                value=row['title_variant'],
                kb_key=row['short_title'],
            )
