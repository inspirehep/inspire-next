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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

import six
import re

from dojson import utils

from inspirehep.config import ARXIV_TO_INSPIRE_CATEGORY_MAPPING as ARXIV_MAP

from inspirehep.dojson.geo_helpers import (country_to_iso_code,
                                           countries_alternative_spellings,
                                           us_state_to_iso_code,
                                           us_states_alternative_spellings,
                                           iso_code_to_country_name,
                                           countries_alternative_codes,
                                           south_korean_cities)

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
    default_server = 'http://inspirehep.net'
    if current_app:
        server = current_app.config.get('SERVER_NAME', default_server)
    else:
        server = default_server
    # This config might also be http://inspirehep.net or
    # https://inspirehep.net.
    if not re.match('^https?://', server):
        server = 'http://{}'.format(server)
    return {'$ref': '{}/api/{}/{}'.format(server, record_type, recid)}


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


RANKS_MAPPINGS = {
    'STAFF': {},
    'SENIOR': {},
    'JUNIOR': {},
    'VISITOR': {
        'alternative_names': ['VISITING SCIENTIST'],
    },
    'POSTDOC': {
        'abbreviations': ['PD']
    },
    'PHD': {
        'alternative_names': ['STUDENT']
    },
    'MASTER': {
        'abbreviations': ['MAS', 'MS', 'MSC']
    },
    'UNDERGRADUATE': {
        'alternative_names': ['BACHELOR'],
        'abbreviations': ['UG', 'BS', 'BA', 'BSC']
    }
}


def classify_rank(value):
    """
    Classifies raw string from rank field as one of the values of RANKS_MAPPINGS
    """
    if not value:
        return None
    elif not isinstance(value, six.string_types):
        return None
    else:
        casted_value = value.upper().replace('.', '')
        for rank_name, rank_mapping in RANKS_MAPPINGS.items():
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


def parse_conference_address(address_string):
    """
    This is a pretty dummy address parser, it only extracts country
    and state (for US) and should be replace with something better
    e.g. Google Geocoding
    """

    geo_elements = address_string.split(',')
    city = geo_elements[0]
    country_name = geo_elements[-1].upper().replace('.', '').strip()
    us_state = None
    state = None
    country_code = None

    # Try to match the country
    country_code = match_country_name_to_its_code(country_name, city)

    if country_code == 'US':
        us_state = match_us_state(geo_elements[-2].upper().strip()
                                  .replace('.', ''))

    if not country_code:
        # sometimes the country name stores info about U.S. state
        us_state = match_us_state(country_name)

    if us_state:
        state = us_state
        country_code = 'US'

    return{
        "original address": address_string,
        "city": None,
        "state": state,
        "country_code": country_code,
        "longitude": None,  # FIXME: we should get it from some geocoding service
        "latitude": None,  # FIXME: same as above
    }


def parse_institution_address(address, city, state_province,
                              country, postal_code, country_code):

    address_string = utils.force_list(address)
    state_province = match_us_state(state_province) or state_province

    postal_code = utils.force_list(postal_code)
    country = utils.force_list(country)
    country_code = match_country_code(country_code)

    if isinstance(postal_code, (tuple, list)):
        postal_code = ', '.join(postal_code)

    if isinstance(city, (tuple, list)):
        city = ', '.join(city)

    if isinstance(country, (tuple, list)):
        country = ', '.join(set(country))

    if not country_code and country:
        country_code = match_country_name_to_its_code(country)

    if not country_code and state_province.startswith('US-'):
        country_code = 'US'

    return {
        'original_address': utils.force_list(address),
        'city': city,
        'state': state_province,
        'country': country,
        'postal_code': postal_code,
        'country_code': country_code,
    }


def match_country_code(original_code):
    if isinstance(original_code, six.string_types):
        original_code = original_code.upper()
        if iso_code_to_country_name.get(original_code):
            return original_code
        else:
            for country_code, alternatives in countries_alternative_codes.items():
                for alternative in alternatives:
                    if original_code == alternative:
                        return country_code
            return None
    else:
        return None


def match_country_name_to_its_code(country_name, city=None):
    """
    Tries to match country name with its code.
    Name of the city helps  when country_name is "Korea".
    """
    if country_name:
        country_name = country_name.upper().replace('.', '').strip()

        if country_to_iso_code.get(country_name):
            return country_to_iso_code.get(country_name)
        elif country_name == 'KOREA':
            if city.upper() in south_korean_cities:
                return 'KR'
        else:
            for c_code, spellings in countries_alternative_spellings.items():
                for spelling in spellings:
                    if country_name == spelling:
                        return c_code

    return None


def match_us_state(state_string):
    "Tries to match string to one of states of the U.S."
    if state_string:
        state_string = state_string.upper().replace('.', '').strip()
        if us_state_to_iso_code.get(state_string):
            return us_state_to_iso_code.get(state_string)
        else:
            for code, state_spellings in us_states_alternative_spellings.items():
                for spelling in state_spellings:
                    if state_string == spelling:
                        return code
    return None


def classify_field(value):
    """ Classifies raw string from field field as one of the values
    of ARXIV_MAP.
    """
    if not value:
        return None
    elif not isinstance(value, (str, unicode)):
        return None
    else:
        casted_value = value.upper()
        for rank_name, rank_mapping in ARXIV_MAP.iteritems():
            if rank_name.upper() == casted_value:
                return rank_mapping
            elif rank_mapping.upper() == casted_value:
                return rank_mapping
        return 'Other'
