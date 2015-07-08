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


@inspiremarc.over('edition', '^250..')
@utils.for_each_value
@utils.filter_values
def edition(self, key, value):
    """Edition Statement."""
    return {
        'value': utils.force_list(
            value.get('a')
        )
    }


@inspiremarc.over('imprint', '^260[_23].')
@utils.for_each_value
@utils.filter_values
def imprint(self, key, value):
    """Publication, Distribution, etc. (Imprint)."""
    return {
        'place': value.get('a'),
        'publisher': value.get('b'),
        'date': value.get('c'),
    }
