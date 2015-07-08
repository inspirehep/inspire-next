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

from ..model import hep


@hep.over('thesis_supervisor', '^701..')
@utils.for_each_value
@utils.filter_values
def thesis_supervisor(self, key, value):
    """The thesis supervisor."""
    return {
        'full_name': value.get('a'),
        'INSPIRE_id': value.get('g'),
        'external_id': value.get('j'),
        'affiliation': value.get('u')
    }


@hep.over('collaboration', '^710[10_2][_2]')
@utils.for_each_value
@utils.filter_values
def collaboration(self, key, value):
    """Added Entry-Corporate Name."""
    return {
        'collaboration': value.get('g')
    }
