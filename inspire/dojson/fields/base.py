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

from ..hep.model import hep
from ..institutions.model import institutions


@institutions.over('control_number', '^001')
@hep.over('control_number', '^001')
def control_number(self, key, value):
    """Record Identifier."""
    return value[0]


@institutions.over('agency_code', '^003')
@hep.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control Number Identifier."""
    return value[0]


@institutions.over('date_and_time_of_latest_transaction', '^005')
@hep.over('date_and_time_of_latest_transaction', '^005')
def date_and_time_of_latest_transaction(self, key, value):
    """Date and Time of Latest Transaction."""
    return value[0]


@hep.over('oai_pmh', '^909C0')
@institutions.over('oai_pmh', '^909C0')
@utils.for_each_value
@utils.filter_values
def oai_pmh(self, key, value):
    """Local OAI-PMH record information."""
    return {
        'id': value.get('o'),
        'set': value.get('p'),
        'previous_set': value.get('q'),
    }


@hep.over('creation_modification_date', '^961..')
@institutions.over('creation_modification_date', '^961..')
@utils.for_each_value
@utils.filter_values
def creation_modification_date(self, key, value):
    """Original creation and modification date."""
    return {
        'modification_date': value.get('c'),
        'creation_date': value.get('x'),
    }


@hep.over('spires_sysno', '^909C0')
@institutions.over('spires_sysno', '^909C0')
@utils.for_each_value
@utils.filter_values
def spires_sysno(self, key, value):
    """Old SPIRES number."""
    return {
        'spires_sysno': value.get('a')
    }


@hep.over('collections', '^980..')
@institutions.over('collections', '^980..')
@utils.for_each_value
@utils.filter_values
def collections(self, key, value):
    """Collection this record belongs to."""
    return {
        'primary': value.get('a'),
        'secondary': value.get('b'),
        'deleted': value.get('c'),
    }


@hep.over('deleted_recid', '^981..')
@institutions.over('deleted_recid', '^981..')
@utils.for_each_value
@utils.filter_values
def deleted_recid(self, key, value):
    """Collection this record belongs to."""
    return {
        'deleted_recid': value.get('a'),
    }
