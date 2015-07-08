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


@inspiremarc.over('oai_pmh', '^909C0')
@utils.for_each_value
@utils.filter_values
def oai_pmh(self, key, value):
    """Local OAI-PMH record information."""
    return {
        'id': value.get('o'),
        'set': value.get('p'),
        'previous_set': value.get('q'),
    }


@inspiremarc.over('creation_modification_date', '^961..')
@utils.for_each_value
@utils.filter_values
def creation_modification_date(self, key, value):
    """Original creation and modification date."""
    return {
        'modification_date': value.get('c'),
        'creation_date': value.get('x'),
    }


@inspiremarc.over('spires_sysno', '^909C0')
@utils.for_each_value
@utils.filter_values
def spires_sysno(self, key, value):
    """Old SPIRES number."""
    return {
        'spires_sysno': value.get('a')
    }


@inspiremarc.over('collections', '^980..')
@utils.for_each_value
@utils.filter_values
def collections(self, key, value):
    """Collection this record belongs to."""
    return {
        'primary': value.get('a'),
        'secondary': value.get('b'),
        'deleted': value.get('c'),
    }


@inspiremarc.over('deleted_recid', '^981..')
@utils.for_each_value
@utils.filter_values
def deleted_recid(self, key, value):
    """Collection this record belongs to."""
    return {
        'deleted_recid': value.get('a'),
    }


@inspiremarc.over('references', '^999C5')
@utils.for_each_value
@utils.filter_values
def references(self, key, value):
    """Produce list of references."""
    return {
        'recid': value.get('0'),
        'texkey': value.get('1'),
        'doi': value.get('a'),
        'collaboration': value.get('c'),
        'editors': value.get('e'),
        'authors': value.get('h'),
        'misc': value.get('m'),
        'number': value.get('o'),
        'isbn': value.get('i'),
        'publisher': value.get('p'),
        'maintitle': value.get('q'),
        'report_number': value.get('r'),
        'title': value.get('t'),
        'url': value.get('u'),
        'journal_pubnote': value.get('s'),
        'raw_reference': value.get('x'),
        'year': value.get('y'),
    }


@inspiremarc.over('refextract', '^999C6')
@utils.for_each_value
@utils.filter_values
def refextract(self, key, value):
    """Contains info from refextract."""
    return {
        'comment': value.get('c'),
        'time': value.get('t'),
        'version': value.get('v'),
        'source': value.get('s'),
    }
