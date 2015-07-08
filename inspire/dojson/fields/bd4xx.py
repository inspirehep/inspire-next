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

from ..model import inspiremarc


@inspiremarc.over('book_series', '^490[10_].')
@utils.for_each_value
@utils.filter_values
def book_series(self, key, value):
    """Book Series."""
    return {
        'value': value.get('a'),
        'volume': value.get('v'),
    }
