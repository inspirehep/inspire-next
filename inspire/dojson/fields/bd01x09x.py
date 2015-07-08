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


@inspiremarc.over('isbn', '^020..')
@utils.for_each_value
@utils.filter_values
def isbn(self, key, value):
    """Other Standard Identifier."""
    return {
        'isbn': value.get('a'),
        'medium': value.get('b')
    }


@inspiremarc.over('doi', '^024[1032478_][10_]')
@utils.for_each_value
@utils.filter_values
def doi(self, key, value):
    """Other Standard Identifier."""
    return {
        'doi': value.get('a')
    }


@inspiremarc.over('system_control_number', '^035..')
@utils.for_each_value
@utils.filter_values
def system_control_number(self, key, value):
    """System Control Number."""
    return {
        'system_control_number': value.get('a'),
        'institute': value.get('9'),
        'obsolete': value.get('z'),
    }


@inspiremarc.over('report_number', '^037..')
@utils.for_each_value
@utils.filter_values
def report_number(self, key, value):
    """Source of Acquisition."""
    return {
        'primary': value.get('a'),
        'arxiv_category': value.get('c'),
        'source': value.get('g')
    }


@inspiremarc.over('language', '^041[10_].')
@utils.for_each_value
@utils.filter_values
def language(self, key, value):
    """Language Code."""
    return {
        'language': value.get('a')
    }


@inspiremarc.over('classification_number', '^084..')
@utils.for_each_value
@utils.filter_values
def classification_number(self, key, value):
    """Other Classification Number."""
    return {
        'classification_number': value.get('a'),
        'standard': value.get('2'),
        'source': value.get('9')
    }
