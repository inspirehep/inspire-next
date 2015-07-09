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

from ..model import experiments


@experiments.over('name', '^119..')
def name(self, key, value):
    """Name of experiment."""
    return value.get("a")


@experiments.over('affiliation', '^119..')
def affiliation(self, key, value):
    """Affiliation of experiment."""
    return value.get("u")


@experiments.over('title', '^245[10_][0_]')
@utils.filter_values
def title(self, key, value):
    """Title Statement."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
        'source': value.get('9'),
    }


@experiments.over('name_variants', '^419..')
@utils.for_each_value
def name_variants(self, key, value):
    """Variants of the name."""
    return value.get('a')


@experiments.over('description', '^520..')
def description(self, key, value):
    """Description of experiment."""
    return value.get("a")


@experiments.over('spokesperson', '^702..')
@utils.for_each_value
def spokesperson(self, key, value):
    """Spokesperson of experiment."""
    return value.get("a")
