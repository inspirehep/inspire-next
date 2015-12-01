# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import uuid

from beard.clustering import block_phonetic

from invenio_records.signals import (
    before_record_index,
    before_record_insert,
)

import numpy as np


@before_record_index.connect
def assign_signature_block(recid, json, *args, **kwargs):
    """Assign phonetic block to each signature.

    The method extends the given signature with a phonetic
    notation of the author's full name, based on
    nysiis algorithm. The phonetic block is assigned before
    the signature is indexed by an elasticsearch instance.
    """
    authors = json.get('authors', [])

    for author in authors:
        if 'full_name' in author:
            name = {'author_name': author['full_name']}

            signature_block = block_phonetic(
                np.array([name], dtype=np.object).reshape(-1, 1),
                threshold=0,
                phonetic_algorithm='nysiis'
            )

            author['signature_block'] = signature_block[0]


@before_record_insert.connect
def assign_uuid(sender, *args, **kwargs):
    """Assign uuid to each signature.

    The method assigns to each signature a universally unique
    identifier based on Python's built-in uuid4. The identifier
    is allocated during the inseration of a new record.
    """
    authors = sender.get('authors', [])

    for author in authors:
        author['uuid'] = str(uuid.uuid4())


@before_record_index.connect
def generate_name_variatons(recid, json, *args, **kwargs):
    """Populates a json record before indexing it to elastic.
    Adds a field for all the possible variations of an authors name

    :param recid: The id of the record that is going to be indexed.
    :param json: The json representation of the record that is going to be
                 indexed.
    """
    from inspirehep.modules.authors.utils import author_tokenize
    authors = json.get("authors")
    if authors:
        for author in authors:
            name = author.get("full_name")
            if name:
                author.update({"name_variations": author_tokenize(name)})
