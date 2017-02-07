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

from __future__ import absolute_import, division, print_function

import json
import uuid

from flask import current_app
import requests

from invenio_indexer.signals import before_record_index
from invenio_records.signals import (
    before_record_insert,
    before_record_update,
)

from .utils import author_tokenize


def _query_beard_api(full_names):
    """Query Beard API.

    This method allows for computation of phonetic blocks
    from a given list of strings.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    text_endpoint = "{base_url}/text/phonetic_blocks".format(
        base_url=current_app.config.get('BEARD_API_URL')
    )

    response = requests.post(
        url=text_endpoint,
        headers=headers,
        data=json.dumps({'full_names': full_names})
    )

    return response.json()['phonetic_blocks']


@before_record_insert.connect
@before_record_update.connect
def assign_phonetic_block(sender, *args, **kwargs):
    """Assign phonetic block to each signature.

    The method extends the given signature with a phonetic
    notation of the author's full name, based on
    nysiis algorithm. The phonetic block is assigned before
    the signature is indexed by an Elasticsearch instance.
    """
    if current_app.config.get('BEARD_API_URL'):
        authors = sender.get('authors', [])
        authors_map = {}

        for index, author in enumerate(authors):
            if 'full_name' in author:
                authors_map[author['full_name']] = index

        # Call Beard API to generate phonetic blocks.
        signatures_blocks = _query_beard_api(authors_map.keys())

        # Add signature block to an author.
        for full_name, signature_block in signatures_blocks.iteritems():
            authors[authors_map[full_name]].update(
                {"signature_block": signature_block})

        # # For missing phonetic blocks (not valid full names) add None.
        for full_name in list(
                set(authors_map.keys()) - set(signatures_blocks.keys())):
            authors[authors_map[full_name]].update(
                {"signature_block": None})


@before_record_insert.connect
@before_record_update.connect
def assign_uuid(sender, *args, **kwargs):
    """Assign uuid to each signature.
    The method assigns to each signature a universally unique
    identifier based on Python's built-in uuid4. The identifier
    is allocated during the insertion of a new record.
    """
    authors = sender.get('authors', [])

    for author in authors:
        # Skip if the author was already populated with a UUID.
        if 'uuid' not in author:
            author['uuid'] = str(uuid.uuid4())


@before_record_index.connect
def generate_name_variations(recid, json, *args, **kwargs):
    """Adds a field with all the possible variations of an authors name.

    :param recid: The id of the record that is going to be indexed.
    :param json: The json representation of the record that is going to be
                 indexed.
    """
    authors = json.get("authors")
    if authors:
        for author in authors:
            name = author.get("full_name")
            if name:
                name_variations = author_tokenize(name)
                author.update({"name_variations": name_variations})
                bai = [
                    item['value'] for item in author.get('ids', [])
                    if item['schema'] == 'INSPIRE BAI'
                ]
                author.update({"name_suggest": {
                    "input": name_variations,
                    "output": name,
                    "payload": {"bai": bai[0] if bai else None}
                }})
