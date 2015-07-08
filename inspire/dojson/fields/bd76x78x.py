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


@inspiremarc.over('publication_info', '^773..')
@utils.for_each_value
@utils.filter_values
def publication_info(self, key, value):
    """Publication info about record."""
    return {
        'recid': value.get('0'),
        'page_artid': value.get('c'),
        'journal_issue': value.get('n'),
        'conf_acronym': value.get('o'),
        'journal_title': value.get('p'),
        'reportnumber': value.get('r'),
        'confpaper_info': value.get('t'),
        'journal_volume': value.get('v'),
        'cnum': value.get('w'),
        'pubinfo_freetext': value.get('x'),
        'year': value.get('y'),
        'isbn': value.get('z'),
    }


@inspiremarc.over('succeeding_entry', '^785..')
@utils.for_each_value
@utils.filter_values
def succeeding_entry(self, key, value):
    """Succeeding Entry."""
    return {
        'relationship_code': value.get('r'),
        'recid': value.get('w'),
        'isbn': value.get('z'),
    }
