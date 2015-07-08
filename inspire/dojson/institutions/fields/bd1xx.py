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


@institutions.over('corporate_author', '^110[10_2].')
@utils.filter_values
def corporate_author(self, key, value):
    """Main Entry-Corporate Name."""
    return {
        'corporate_author': value.get('a'),
    }


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
