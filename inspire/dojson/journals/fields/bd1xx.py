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

from ..model import journals


@journals.over('issn', '^022..')
def issn(self, key, value):
    """ISSN Statement."""
    return value.get("a")


@journals.over('coden', '^030..')
def coden(self, key, value):
    """CODEN Statement."""
    return value.get("a")


@journals.over('title', '^130..')
@utils.filter_values
def title(self, key, value):
    """Title Statement."""
    return {
        'title': value.get('a'),
    }


@journals.over('short_title', '^711..')
@utils.for_each_value
@utils.filter_values
def short_title(self, key, value):
    """Title Statement."""
    return {
        'short_title': value.get('a'),
    }


@journals.over('name_variants', '^730..')
@utils.for_each_value
def name_variants(self, key, value):
    """Variants of the name."""
    return value.get('a')
