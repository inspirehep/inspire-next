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


@inspiremarc.over('title_variation', '^210[10_][0_]')
@utils.for_each_value
@utils.filter_values
def title_variation(self, key, value):
    """Title variation."""
    return {
        'value': utils.force_list(
            value.get('a')
        )
    }


@inspiremarc.over('title_translation', '^242[10_][0_]')
@utils.for_each_value
@utils.filter_values
def title_translation(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'value': utils.force_list(
            value.get('a')
        ),
        'subtitle': utils.force_list(
            value.get('b')
        )
    }


@inspiremarc.over('title', '^245[10_][0_]')
@utils.filter_values
def title(self, key, value):
    """Title Statement."""
    return {
        'title': utils.force_list(
            value.get('a')
        ),
        'subtitle': utils.force_list(
            value.get('b')
        ),
        'source': value.get('9'),
    }


@inspiremarc.over('title_arxiv', '^246[1032_][_103254768]')
@utils.for_each_value
@utils.filter_values
def title_arxiv(self, key, value):
    """Varying Form of Title."""
    return {
        'title': utils.force_list(
            value.get('a')
        ),
        'subtitle': utils.force_list(
            value.get('b')
        ),
        'source': value.get('9'),
    }


@inspiremarc.over('title_old', '^247[10_][10_]')
@utils.for_each_value
@utils.filter_values
def title_old(self, key, value):
    """Former Title."""
    return {
        'title': utils.force_list(
            value.get('a')
        ),
        'subtitle': utils.force_list(
            value.get('b')
        ),
        'source': value.get('9'),
    }
