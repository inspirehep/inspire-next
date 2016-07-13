# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON related utilities."""

from __future__ import absolute_import, division, print_function

import re
import six

try:
    from flask import current_app
except ImportError:  # pragma: no cover
    current_app = None

from dojson.utils import force_list

from inspirehep.config import (
    ARXIV_TO_INSPIRE_CATEGORY_MAPPING,
    INSPIRE_RANK_TYPES,
)

from inspirehep.utils.dedupers import dedupe_list, dedupe_list_of_dicts


_RE_2_CHARS = re.compile(r"[a-z].*[a-z]", re.I)


def classify_field(value):
    """Classify value as a key of ARXIV_TO_INSPIRE_CATEGORY_MAPPING."""
    if not value:
        return None
    elif not isinstance(value, six.string_types):
        return None
    else:
        casted_value = value.upper()
        for name, category in six.iteritems(ARXIV_TO_INSPIRE_CATEGORY_MAPPING):
            if name.upper() == casted_value:
                return category
            elif category.upper() == casted_value:
                return category
        return 'Other'


def classify_rank(value):
    """Classify raw string as one of the keys in INSPIRE_RANK_TYPES."""
    if not value:
        return None
    elif not isinstance(value, six.string_types):
        return None
    else:
        casted_value = value.upper().replace('.', '')
        for rank_name, rank_mapping in INSPIRE_RANK_TYPES.items():
            if rank_name in casted_value:
                return rank_name
            else:
                if rank_mapping.get('alternative_names'):
                    for alternative in rank_mapping['alternative_names']:
                        if alternative in casted_value:
                            return rank_name
                if rank_mapping.get('abbreviations'):
                    for abbrev in rank_mapping['abbreviations']:
                        if abbrev == casted_value:
                            return rank_name

        return 'OTHER'


def create_profile_url(profile_id):
    """Create HEP author profile link based on the profile_id."""
    base_url = 'http://inspirehep.net/record/'

    try:
        int(profile_id)
        return base_url + str(profile_id)
    except (TypeError, ValueError):
        return ''


def force_single_element(obj):
    """Force an object to a list and return the first element."""
    lst = force_list(obj)
    if lst:
        return lst[0]
    return None


def get_int_value(d, k):
    """Get a value in a dict and cast it to int if possible."""
    try:
        return int(d.get(k))
    except (TypeError, ValueError):
        return None


def get_recid_from_ref(ref_obj):
    """Retrieve recid from jsonref reference object.

    If no recid can be parsed, return None.
    """
    if not isinstance(ref_obj, dict):
        return None
    url = ref_obj.get('$ref', '')
    try:
        res = int(url.split('/')[-1])
    except ValueError:
        res = None
    return res


def get_record_ref(recid, record_type='record'):
    """Create record jsonref reference object from recid.

    None recids will return a None object.
    Valid recids will return an object in the form of:
        {'$ref': url_for_record}
    """
    if recid is None:
        return None
    default_server = 'http://inspirehep.net'
    if current_app:
        server = current_app.config.get('SERVER_NAME') or default_server
    else:
        server = default_server
    # This config might also be http://inspirehep.net or
    # https://inspirehep.net.
    if not re.match('^https?://', server):
        server = 'http://{}'.format(server)
    return {'$ref': '{}/api/{}/{}'.format(server, record_type, recid)}


def legacy_export_as_marc(json, tabsize=4):
    """Create the MARCXML representation using the producer rules."""

    def encode_for_marcxml(value):
        from invenio_utils.text import encode_for_xml
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return encode_for_xml(str(value), wash=True)

    export = ['<record>\n']

    for key, value in sorted(six.iteritems(json)):
        if not value:
            continue
        if key.startswith('00') and len(key) == 3:
            # Controlfield
            if isinstance(value, (tuple, list)):
                value = value[0]
            export += ['\t<controlfield tag="%s">%s'
                       '</controlfield>\n'.expandtabs(tabsize)
                       % (key, encode_for_marcxml(value))]
        else:
            tag = key[:3]
            try:
                ind1 = key[3].replace("_", "")
            except:
                ind1 = ""
            try:
                ind2 = key[4].replace("_", "")
            except:
                ind2 = ""
            if isinstance(value, dict):
                value = [value]
            for field in value:
                export += ['\t<datafield tag="%s" ind1="%s" '
                           'ind2="%s">\n'.expandtabs(tabsize)
                           % (tag, ind1, ind2)]
                if field:
                    for code, subfieldvalue in six.iteritems(field):
                        if subfieldvalue:
                            if isinstance(subfieldvalue, (list, tuple)):
                                for val in subfieldvalue:
                                    export += ['\t\t<subfield code="%s">%s'
                                               '</subfield>\n'.expandtabs(tabsize)
                                               % (code, encode_for_marcxml(val))]
                            else:
                                export += ['\t\t<subfield code="%s">%s'
                                           '</subfield>\n'.expandtabs(tabsize)
                                           % (code,
                                              encode_for_marcxml(subfieldvalue))]
                export += ['\t</datafield>\n'.expandtabs(tabsize)]
    export += ['</record>\n']
    return "".join(export)


def strip_empty_values(obj):
    """Recursively strips empty values."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            new_val = strip_empty_values(val)
            # There are already lots of leaks in the callers of this function,
            # there's no need to make it idempotent and double memory.
            if new_val is not None:
                obj[key] = new_val
            else:
                del obj[key]
        return obj or None
    elif isinstance(obj, (list, tuple, set)):
        new_obj = []
        for val in obj:
            new_val = strip_empty_values(val)
            if new_val is not None:
                new_obj.append(new_val)
        return type(obj)(new_obj) or None
    elif obj or obj is False or obj == 0:
        return obj
    else:
        return None


def dedupe_all_lists(obj):
    """Recursively remove duplucates from all lists."""
    squared_dedupe_len = 10
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = dedupe_all_lists(value)
        return obj
    elif isinstance(obj, (list, tuple, set)):
        new_elements = [dedupe_all_lists(v) for v in obj]
        if len(new_elements) < squared_dedupe_len:
            new_obj = dedupe_list(new_elements)
        else:
            new_obj = dedupe_list_of_dicts(new_elements)
        return type(obj)(new_obj)
    else:
        return obj


def clean_record(rec):
    return dedupe_all_lists(strip_empty_values(rec))


def split_page_artid(page_artid):
    """Split page_artid into page_start/end and artid."""
    page_start = None
    page_end = None
    artid = None

    for page_artid in force_list(page_artid) or []:
        if page_artid:
            if '-' in page_artid:
                # if it has a dash it's a page range
                page_range = page_artid.split('-')
                if len(page_range) == 2:
                    page_start, page_end = page_range
                else:
                    artid = page_artid
            elif _RE_2_CHARS.search(page_artid):
                # if it it has 2 ore more letters it's an article ID
                artid = page_artid
            elif len(page_artid) >= 5:
                # it it is longer than 5 digits it's an article ID
                artid = page_artid
            else:
                if artid is None:
                    artid = page_artid
                if page_start is None:
                    page_start = page_artid

    return page_start, page_end, artid
