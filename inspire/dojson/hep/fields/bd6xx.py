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


@hep.over('subject_term', '^650[1_][_7]')
@utils.for_each_value
@utils.filter_values
def subject_term(self, key, value):
    """Subject Added Entry-Topical Term."""
    return {
        'value': value.get('a'),
        'scheme': value.get('2'),
        'source': value.get('9'),
    }


@hep.over('free_keyword', '^653[10_2][_1032546]')
@utils.for_each_value
@utils.filter_values
def free_keyword(self, key, value):
    """Free keywords."""
    return {
        'value': value.get('a'),
        'source': value.get('9'),
    }


@hep.over('accelerator_experiment', '^693..')
@utils.for_each_value
@utils.filter_values
def accelerator_experiment(self, key, value):
    """The accelerator/experiment related to this record."""
    return {
        'accelerator': value.get('a'),
        'experiment': value.get('e'),
    }


@hep.over('thesaurus_terms', '^695..')
@utils.for_each_value
@utils.filter_values
def thesaurus_terms(self, key, value):
    """Controlled keywords."""
    return {
        'keyword': value.get('a'),
        'energy_range': value.get('e'),
        'classification_scheme': value.get('2'),
    }
