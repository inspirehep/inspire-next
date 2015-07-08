# -*- coding: utf-8 -*-
#
# This file is part of DoJSON
# Copyright (C) 2015 CERN.
#
# DoJSON is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""MARC 21 model definition."""

from ..model import inspiremarc


@inspiremarc.over('control_number', '^001')
def control_number(self, key, value):
    """Control Number."""
    return value[0]


@inspiremarc.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control Number Identifier."""
    return value[0]


@inspiremarc.over('date_and_time_of_latest_transaction', '^005')
def date_and_time_of_latest_transaction(self, key, value):
    """Date and Time of Latest Transaction."""
    return value[0]
