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

from ..hep.model import hep, hep2marc
from ..institutions.model import institutions
from ..experiments.model import experiments
from ..journals.model import journals


@institutions.over('control_number', '^001')
@hep.over('control_number', '^001')
@experiments.over('control_number', '^001')
@journals.over('control_number', '^001')
def control_number(self, key, value):
    """Record Identifier."""
    return value[0]


@hep2marc.over('001', 'control_number')
def control_number2marc(self, key, value):
    """Record Identifier."""
    return value


@institutions.over('agency_code', '^003')
@hep.over('agency_code', '^003')
@experiments.over('agency_code', '^003')
@journals.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control Number Identifier."""
    return value[0]


@hep2marc.over('003', 'agency_code')
def agency_code2marc(self, key, value):
    """Control Number Identifier."""
    return value


@institutions.over('date_and_time_of_latest_transaction', '^005')
@hep.over('date_and_time_of_latest_transaction', '^005')
@experiments.over('date_and_time_of_latest_transaction', '^005')
@journals.over('date_and_time_of_latest_transaction', '^005')
def date_and_time_of_latest_transaction(self, key, value):
    """Date and Time of Latest Transaction."""
    return value[0]


@hep2marc.over('005', 'date_and_time_of_latest_transaction')
def date_and_time_of_latest_transaction2marc(self, key, value):
    """Date and Time of Latest Transaction."""
    return value


@institutions.over('url', '^856.[10_28]')
@experiments.over('url', '^856.[10_28]')
@journals.over('url', '^856.[10_28]')
@hep.over('url', '^856.[10_28]')
@utils.for_each_value
@utils.filter_values
def url(self, key, value):
    """URL to external resource."""
    return {
        'url': value.get('u'),
        'doc_string': value.get('w'),
        'description': value.get('y'),
        'material_type': value.get('3'),
        'comment': value.get('z'),
        'name': value.get('f'),
        'size': value.get('s'),
    }


@hep2marc.over('8564', 'url')
@utils.for_each_value
@utils.filter_values
def url2marc(self, key, value):
    """URL to external resource."""
    return {
        'u': value.get('url'),
        'w': value.get('doc_string'),
        'y': value.get('description'),
        '3': value.get('material_type'),
        'z': value.get('comment'),
        'f': value.get('name'),
        's': value.get('size'),
    }


@hep.over('oai_pmh', '^909C0')
@institutions.over('oai_pmh', '^909C0')
@experiments.over('oai_pmh', '^909C0')
@journals.over('oai_pmh', '^909C0')
@utils.for_each_value
@utils.filter_values
def oai_pmh(self, key, value):
    """Local OAI-PMH record information."""
    return {
        'id': value.get('o'),
        'set': value.get('p'),
        'previous_set': value.get('q'),
    }


@hep2marc.over('909C0', 'oai_pmh')
@utils.for_each_value
@utils.filter_values
def oai_pmh2marc(self, key, value):
    """Local OAI-PMH record information."""
    return {
        'o': value.get('id'),
        'p': value.get('set'),
        'q': value.get('previous_set')
    }


@hep.over('creation_modification_date', '^961..')
@institutions.over('creation_modification_date', '^961..')
@experiments.over('creation_modification_date', '^961..')
@journals.over('creation_modification_date', '^961..')
@utils.for_each_value
@utils.filter_values
def creation_modification_date(self, key, value):
    """Original creation and modification date."""
    return {
        'modification_date': value.get('c'),
        'creation_date': value.get('x'),
    }


@hep2marc.over('961', 'creation_modification_date')
@utils.for_each_value
@utils.filter_values
def creation_modification_date2marc(self, key, value):
    """Original creation and modification date."""
    return {
        'c': value.get('modification_date'),
        'x': value.get('creation_date')
    }


@hep.over('spires_sysno', '^970..')
@institutions.over('spires_sysno', '^970..')
@experiments.over('spires_sysno', '^970..')
@journals.over('spires_sysno', '^970..')
@utils.for_each_value
@utils.filter_values
def spires_sysno(self, key, value):
    """Old SPIRES number."""
    return {
        'spires_sysno': value.get('a')
    }


@hep2marc.over('970', 'spires_sysno')
@utils.for_each_value
@utils.filter_values
def spires_sysno2marc(self, key, value):
    """Old SPIRES number."""
    return {
        'a': value.get('spires_sysno')
    }


@hep.over('collections', '^980..')
@institutions.over('collections', '^980..')
@experiments.over('collections', '^980..')
@journals.over('collections', '^980..')
@utils.for_each_value
@utils.filter_values
def collections(self, key, value):
    """Collection this record belongs to."""
    return {
        'primary': value.get('a'),
        'secondary': value.get('b'),
        'deleted': value.get('c'),
    }


@hep2marc.over('980', 'collections')
@utils.for_each_value
@utils.filter_values
def collections2marc(self, key, value):
    """Collection this record belongs to."""
    return {
        'a': value.get('primary'),
        'b': value.get('secondary'),
        'c': value.get('deleted')
    }


@hep.over('deleted_recid', '^981..')
@institutions.over('deleted_recid', '^981..')
@experiments.over('deleted_recid', '^981..')
@journals.over('deleted_recid', '^981..')
@utils.for_each_value
@utils.filter_values
def deleted_recid(self, key, value):
    """Collection this record belongs to."""
    return {
        'deleted_recid': value.get('a'),
    }


@hep2marc.over('981', 'deleted_recid')
@utils.for_each_value
@utils.filter_values
def deleted_recid2marc(self, key, value):
    """Collection this record belongs to."""
    return {
        'a': value.get('deleted_recid'),
    }
