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


@inspiremarc.over('url', '^856.[10_28]')
@utils.for_each_value
@utils.filter_values
def url(self, key, value):
    """URL to external resource."""
    return {
        'url': value.get('u'),
        'doc_string': value.get('w'),
        'description': value.get('y'),
        'material_type': value.get('3'),
        'comment': value.get('z'),
        'name': value.get('f'),
        'size': value.get('s'),
    }
