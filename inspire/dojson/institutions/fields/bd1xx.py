# -*- coding: utf-8 -*-
#
# This file is part of DoJSON
# Copyright (C) 2015 CERN.
#
# DoJSON is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""MARC 21 model definition."""

from dojson import utils

from ..model import institutions


@institutions.over('location', '^034..')
@utils.filter_values
def location(self, key, value):
    """GPS location info."""
    return {
        'longitude': value.get('d'),
        'latitude': value.get('f')
    }


@institutions.over('timezone', '^043..')
def timezone(self, key, value):
    """Timezone."""
    return value.get('t')


@institutions.over('name', '^110..')
def name(self, key, value):
    """List of names."""
    names = utils.force_list(value.get('a')) or []
    names.extend(utils.force_list(value.get('u')) or [])
    names.extend(utils.force_list(value.get('t')) or [])
    return names


@institutions.over('institution', '^110..')
@utils.filter_values
def institution(self, key, value):
    """Institution info."""
    return {
        'name': value.get('a'),
        'department': value.get('b'),
        'new_name': value.get('t'),
        'affiliation': value.get('u'),
        'obsolete_icn': value.get('x'),
    }


@institutions.over('address', '^371..')
@utils.for_each_value
@utils.filter_values
def address(self, key, value):
    """Address info."""
    return {
        'address': value.get('a'),
        'city': value.get('b'),
        'state': value.get('c'),
        'country': value.get('d'),
        'postal_code': value.get('e'),
        'country_code': value.get('g'),
    }


@institutions.over('activity', '^372..')
def activity(self, key, value):
    """Field of activity."""
    return value.get('a')


@institutions.over('name_variants', '^410..')
@utils.for_each_value
def name_variants(self, key, value):
    """Variants of the name."""
    return value.get('a')


@institutions.over('core', '^690C.')
def core(self, key, value):
    """Check if it is a CORE institution."""
    return value.get('a', "").upper() == "CORE"
