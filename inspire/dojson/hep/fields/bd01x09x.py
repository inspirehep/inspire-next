# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""MARC 21 model definition."""

from dojson import utils

from ..model import hep, hep2marc


@hep.over('isbn', '^020..')
@utils.for_each_value
@utils.filter_values
def isbn(self, key, value):
    """Other Standard Identifier."""
    return {
        'isbn': value.get('a'),
        'medium': value.get('b')
    }


@hep2marc.over('020', 'isbn')
@utils.for_each_value
@utils.filter_values
def isbn2marc(self, key, value):
    """Other Standard Identifier."""
    return {
        'a': value.get('isbn'),
        'b': value.get('medium'),
    }


@hep.over('doi', '^024[1032478_][10_]')
@utils.for_each_value
@utils.filter_values
def doi(self, key, value):
    """Other Standard Identifier."""
    return {
        'doi': value.get('a')
    }


@hep2marc.over('024', 'doi')
@utils.for_each_value
@utils.filter_values
def doi2marc(self, key, value):
    """Other Standard Identifier."""
    return {
        'a': value.get('doi'),
    }


@hep.over('system_control_number', '^035..')
@utils.for_each_value
@utils.filter_values
def system_control_number(self, key, value):
    """System Control Number."""
    return {
        'system_control_number': value.get('a'),
        'institute': value.get('9'),
        'obsolete': value.get('z'),
    }


@hep2marc.over('035', 'system_control_number')
@utils.for_each_value
@utils.filter_values
def system_control_number2marc(self, key, value):
    """System Control Number."""
    return {
        'a': value.get('system_control_number'),
        '9': value.get('institute'),
        'z': value.get('obsolete'),
    }


@hep.over('report_number', '^037..')
@utils.for_each_value
@utils.filter_values
def report_number(self, key, value):
    """Source of Acquisition."""
    return {
        'primary': value.get('a'),
        'arxiv_category': value.get('c'),
        'source': value.get('g')
    }


@hep2marc.over('037', 'report_number')
@utils.for_each_value
@utils.filter_values
def report_number2marc(self, key, value):
    """Source of Acquisition."""
    return {
        'a': value.get('primary'),
        'c': value.get('arxiv_category'),
        'g': value.get('source'),
    }


@hep.over('language', '^041[10_].')
@utils.for_each_value
@utils.filter_values
def language(self, key, value):
    """Language Code."""
    return {
        'language': value.get('a')
    }


@hep2marc.over('041', 'language')
@utils.for_each_value
@utils.filter_values
def language2marc(self, key, value):
    """Language Code."""
    return {
        'a': value.get('language'),
    }


@hep.over('classification_number', '^084..')
@utils.for_each_value
@utils.filter_values
def classification_number(self, key, value):
    """Other Classification Number."""
    return {
        'classification_number': value.get('a'),
        'standard': value.get('2'),
        'source': value.get('9')
    }


@hep2marc.over('084', 'classification_number')
@utils.for_each_value
@utils.filter_values
def classification_number2marc(self, key, value):
    """Other Classification Number."""
    return {
        'a': value.get('classification_number'),
        '2': value.get('standard'),
        '9': value.get('source'),
    }
