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
import re
from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_records.models import RecordMetadata
from sqlalchemy import cast, not_, type_coerce
from sqlalchemy.dialects.postgresql import JSONB
from inspirehep.modules.refextract.utils import KbWriter

RE_PUNCTUATION = re.compile(r"[\.,;'\(\)-]", re.UNICODE)


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
            (r.json -> '_collections')::jsonb ? 'Journals' AND ((r.json -> 'deleted') IS NULL OR (r.json -> 'deleted') != 'true'::jsonb)
    """)

    title_variants_query = db.session.execute("""
        SELECT
            r.json -> 'short_title' AS short_title,
            jsonb_array_elements((r.json -> 'title_variants')::jsonb) AS title_variant
        FROM
            records_metadata AS r
        WHERE
            (r.json -> '_collections')::jsonb ? 'Journals' AND ((r.json -> 'deleted') IS NULL OR (r.json -> 'deleted') != 'true'::jsonb)
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


def normalize_title(raw_title):
    """
    Returns the normalised raw_title. Normalising means removing all non alphanumeric characters,
    collapsing all contiguous whitespace to one space and uppercasing the resulting string.
    """
    if not raw_title:
        return

    normalized_title = RE_PUNCTUATION.sub(" ", raw_title)
    normalized_title = " ".join(normalized_title.split())
    normalized_title = normalized_title.upper()

    return normalized_title


def create_journal_kb_dict():
    """
    Returns a dictionary that is populated with refextracts's journal KB from the database.
        { SOURCE: DESTINATION }
    which represents that ``SOURCE`` is translated to ``DESTINATION`` when found.
    Note that refextract expects ``SOURCE`` to be normalized, which means removing
    all non alphanumeric characters, collapsing all contiguous whitespace to one
    space and uppercasing the resulting string.
    """
    only_journals = type_coerce(RecordMetadata.json, JSONB)["_collections"].contains(
        ["Journals"]
    )
    only_not_deleted = not_(
        type_coerce(RecordMetadata.json, JSONB).has_key("deleted")  # noqa
    ) | not_(  # noqa
        type_coerce(RecordMetadata.json, JSONB)["deleted"] == cast(True, JSONB)
    )
    entity_short_title = RecordMetadata.json["short_title"]
    entity_journal_title = RecordMetadata.json["journal_title"]["title"]
    entity_title_variants = RecordMetadata.json["title_variants"]

    titles_query = RecordMetadata.query.with_entities(
        entity_short_title, entity_journal_title
    ).filter(only_journals, only_not_deleted)

    title_variants_query = RecordMetadata.query.with_entities(
        entity_short_title, entity_title_variants
    ).filter(only_journals, only_not_deleted)

    title_dict = {}

    for (short_title, journal_title) in titles_query.all():
        title_dict[normalize_title(short_title)] = short_title
        title_dict[normalize_title(journal_title)] = short_title

    for (short_title, title_variants) in title_variants_query.all():
        if title_variants is None:
            continue

        sub_dict = {
            normalize_title(title_variant): short_title
            for title_variant in title_variants
        }

        title_dict.update(sub_dict)

    return title_dict
