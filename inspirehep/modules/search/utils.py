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

"""Results class to wrap a query and allow for searching."""

import json

from flask import current_app

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


def dotter(d, key, dots):
    """ Given a json schema dictionary (d argument) returns all the properties
        in a dotted notation.
        e.g
        author
        author.full_name
        author.affiliation
        etc...
    """
    if isinstance(d, dict):
        if 'items' in d:
            dots.append(key)
            dotter(d['items'], key, dots)
        elif 'properties' in d:
            dotter(d['properties'], key, dots)
        else:
            for k in d:
                dotter(d[k], key + '.' + k, dots)
    else:
        dots.append(key)
    return dots


def get_dotted_keys(d, key, dots):
    """Removes undesirable information from extracted keywords."""
    dotted_keys = dotter(d, key, dots)
    return set(dotted_key[1:].rsplit('.', 1)[0] for dotted_key in dotted_keys)


@lru_cache(maxsize=1000)
def generate_valid_keywords():
    """Parses all sources that contain valid search keywords to a list."""
    valid_keywords = []

    keyword_mapping = current_app.config['SEARCH_ELASTIC_KEYWORD_MAPPING']

    # Get keywords from configuration file
    keywords = keyword_mapping.keys()
    for k in keyword_mapping.values():
        if isinstance(k, dict):
            keywords += k.keys()
    # Get keywords from the json schema
    for path in current_app.extensions['invenio-jsonschemas'].list_schemas():
        data = current_app.extensions['invenio-jsonschemas'].get_schema(path)
        data = data.get('properties')
        dotted_keywords = get_dotted_keys(data, '', [])
        keywords += dotted_keywords

    # Get keywords from elasticsearch mapping
    for name, path in current_app.extensions['invenio-search'].mappings.iteritems():
        with open(path) as data_file:
            data = json.load(data_file)
        data = data.get('mappings').get(name.split('-')[-1]).get('properties')
        dotted_keywords = get_dotted_keys(data, '', [])
        keywords += dotted_keywords
    cleaned_keywords = list(set([k for k in keywords if k is not None]))
    # Sort by longest string descending
    cleaned_keywords.sort(key=len, reverse=True)
    return cleaned_keywords
