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

"""DoJSON related utilities."""

import pkg_resources
import six

try:
    from flask import current_app
except ImportError:
    current_app = None


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


def create_profile_url(profile_id):
    """Create HEP author profile link based on the profile_id."""
    base_url = 'http://inspirehep.net/record/'

    try:
        int(profile_id)
        return base_url + str(profile_id)
    except (TypeError, ValueError):
        return ''


def strip_empty_values(obj):
    """Recursively strips empty values."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            value = strip_empty_values(value)
            if value or value is False or value == 0:
                obj[key] = value
            else:
                del obj[key]
        return obj
    elif isinstance(obj, (list, tuple, set)):
        new_obj = [strip_empty_values(v) for v in obj]
        new_obj = [v for v in new_obj if v or v is False or v == 0]
        return type(obj)(new_obj)
    else:
        return obj


def remove_duplicates_from_list(l):
    """Remove duplicates from a list preserving the order.

    We might be tempted to use the list(set(l)) idiom,
    but it doesn't preserve the order, which hinders
    testability."""
    result = []

    for el in l:
        if el not in result:
            result.append(el)

    return result


def remove_duplicates_from_list_of_dicts(ld):
    """Remove duplicates from a list of dictionaries preserving the order.

    We can't use the generic list helper because a dictionary isn't
    hashable. Taken from http://stackoverflow.com/a/9427216/374865."""
    result = []
    seen = set()

    for d in ld:
        t = tuple(d.items())
        if t not in seen:
            result.append(d)
            seen.add(t)

    return result


def get_record_ref(recid, record_type='record'):
    """Create record jsonref reference object from recid.

    None recids will return a None object.
    Valid recids will return an object in the form of:
        {'$ref': url_for_record}
    """
    if recid is None:
        return None
    default_server = 'inspirehep.net'
    if current_app:
        server = current_app.config.get('SERVER_NAME', default_server)
    else:
        server = default_server
    return {'$ref': 'http://{}/api/{}/{}'.format(server, record_type, recid)}


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
