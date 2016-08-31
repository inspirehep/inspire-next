# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

from __future__ import absolute_import, division, print_function

from dojson import utils
from dojson.errors import IgnoreKey

from ..conferences.model import conferences
from ..experiments.model import experiments
from ..hep.model import hep, hep2marc
from ..hepnames.model import hepnames, hepnames2marc
from ..institutions.model import institutions
from ..jobs.model import jobs
from ..journals.model import journals
from ..utils import (
    classify_field,
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
)

from inspirehep.utils.helpers import force_force_list


def self_url(index):
    def _self_url(self, key, value):
        """Url of the record itself."""
        self['control_number'] = value
        return get_record_ref(value, index)
    return _self_url

institutions.over('self', '^001')(self_url('institutions'))
hep.over('self', '^001')(self_url('literature'))
conferences.over('self', '^001')(self_url('conferences'))
experiments.over('self', '^001')(self_url('experiments'))
journals.over('self', '^001')(self_url('journals'))
hepnames.over('self', '^001')(self_url('authors'))
jobs.over('self', '^001')(self_url('jobs'))


@hep2marc.over('001', 'control_number')
@hepnames2marc.over('001', 'control_number')
def control_number2marc(self, key, value):
    """Record Identifier."""
    return value


@institutions.over('agency_code', '^003')
@hep.over('agency_code', '^003')
@conferences.over('agency_code', '^003')
@experiments.over('agency_code', '^003')
@journals.over('agency_code', '^003')
@hepnames.over('agency_code', '^003')
@jobs.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control Number Identifier."""
    return value


@hep2marc.over('003', 'agency_code')
@hepnames2marc.over('003', 'agency_code')
def agency_code2marc(self, key, value):
    """Control Number Identifier."""
    return value


@institutions.over('date_and_time_of_latest_transaction', '^005')
@hep.over('date_and_time_of_latest_transaction', '^005')
@conferences.over('date_and_time_of_latest_transaction', '^005')
@experiments.over('date_and_time_of_latest_transaction', '^005')
@journals.over('date_and_time_of_latest_transaction', '^005')
@hepnames.over('date_and_time_of_latest_transaction', '^005')
@jobs.over('date_and_time_of_latest_transaction', '^005')
def date_and_time_of_latest_transaction(self, key, value):
    """Date and Time of Latest Transaction."""
    return value


@hep2marc.over('005', 'date_and_time_of_latest_transaction')
@hepnames2marc.over('005', 'date_and_time_of_latest_transaction')
def date_and_time_of_latest_transaction2marc(self, key, value):
    """Date and Time of Latest Transaction."""
    return value


@hep.over('creation_modification_date', '^961..')
@conferences.over('creation_modification_date', '^961..')
@institutions.over('creation_modification_date', '^961..')
@experiments.over('creation_modification_date', '^961..')
@journals.over('creation_modification_date', '^961..')
@hepnames.over('creation_modification_date', '^961..')
@jobs.over('creation_modification_date', '^961..')
@utils.for_each_value
@utils.filter_values
def creation_modification_date(self, key, value):
    """Original creation and modification date."""
    return {
        'modification_date': value.get('c'),
        'creation_date': value.get('x'),
    }


@hep2marc.over('961', 'creation_modification_date')
@hepnames2marc.over('961', 'creation_modification_date')
@utils.for_each_value
@utils.filter_values
def creation_modification_date2marc(self, key, value):
    """Original creation and modification date."""
    return {
        'c': value.get('modification_date'),
        'x': value.get('creation_date')
    }


@hep.over('spires_sysnos', '^970..')
@conferences.over('spires_sysnos', '^970..')
@institutions.over('spires_sysnos', '^970..')
@experiments.over('spires_sysnos', '^970..')
@journals.over('spires_sysnos', '^970..')
@hepnames.over('spires_sysnos', '^970..')
@jobs.over('spires_sysnos', '^970..')
@utils.ignore_value
def spires_sysnos(self, key, value):
    """Old SPIRES number and new_recid from 970."""
    external_system_numbers = self.get('external_system_numbers', [])
    value = force_force_list(value)
    new_recid = None
    for val in value:
        for sysno in force_force_list(val.get('a')):
            if sysno:
                external_system_numbers.append(
                    {
                        "institute": "SPIRES",
                        "value": sysno,
                        "obsolete": True
                    }
                )
        if 'd' in val:
            new_recid = val.get('d')
    if new_recid is not None:
        self['new_record'] = get_record_ref(new_recid)

    self['external_system_numbers'] = external_system_numbers


@hep2marc.over('970', 'new_record')
@hepnames2marc.over('970', 'new_record')
def spires_sysnos2marc(self, key, value):
    """970 SPIRES number and new recid."""
    value = force_force_list(value)
    existing_values = self.get('970', [])

    val_recids = [get_recid_from_ref(val) for val in value]
    existing_values.extend(
        [{'d': val} for val in val_recids if val]
    )
    return existing_values


@hep.over('collections', '^980..')
@conferences.over('collections', '^980..')
@institutions.over('collections', '^980..')
@experiments.over('collections', '^980..')
@journals.over('collections', '^980..')
@hepnames.over('collections', '^980..')
@jobs.over('collections', '^980..')
def collections(self, key, value):
    """Collection this record belongs to."""
    value = force_force_list(value)

    def get_value(value):
        primary = force_single_element(value.get('a'))
        return {
            'primary': primary,
            'secondary': value.get('b'),
            'deleted': value.get('c'),
        }

    collections = self.get('collections', [])

    for val in value:
        collections.append(get_value(val))

    return collections


@hep2marc.over('980', 'collections')
@hepnames2marc.over('980', 'collections')
@utils.for_each_value
@utils.filter_values
def collections2marc(self, key, value):
    """Collection this record belongs to."""
    return {
        'a': value.get('primary'),
        'b': value.get('secondary'),
        'c': value.get('deleted')
    }


@hep.over('deleted_records', '^981..')
@conferences.over('deleted_records', '^981..')
@institutions.over('deleted_records', '^981..')
@experiments.over('deleted_records', '^981..')
@journals.over('deleted_records', '^981..')
@hepnames.over('deleted_records', '^981..')
@jobs.over('deleted_records', '^981..')
@utils.for_each_value
@utils.ignore_value
def deleted_records(self, key, value):
    """Recid of deleted record this record is master for."""
    # FIXME we are currently using the default /record API. Which might
    # resolve to a 404 response.
    return get_record_ref(value.get('a'))


@hep.over('fft', '^FFT..')
@conferences.over('fft', '^FFT..')
@institutions.over('fft', '^FFT..')
@experiments.over('fft', '^FFT..')
@journals.over('fft', '^FFT..')
@utils.for_each_value
@utils.filter_values
def fft(self, key, value):
    """Collection this record belongs to."""
    return {
        'url': value.get('a'),
        'docfile_type': value.get('t'),
        'flag': value.get('o'),
        'description': value.get('d'),
        'filename': value.get('n'),
    }


@hep.over('FFT', 'fft')
@conferences.over('FFT', 'fft')
@institutions.over('FFT', 'fft')
@experiments.over('FFT', 'fft')
@journals.over('FFT', 'fft')
@utils.for_each_value
@utils.filter_values
def fft2marc(self, key, value):
    """Collection this record belongs to."""
    return {
        'a': value.get('url'),
        't': value.get('docfile_type'),
        'o': value.get('flag'),
        'd': value.get('description'),
        'n': value.get('filename'),
    }


@hep2marc.over('981', 'deleted_records')
@hepnames2marc.over('981', 'deleted_records')
@utils.for_each_value
@utils.filter_values
def deleted_records2marc(self, key, value):
    """Deleted recids."""
    return {
        'a': get_recid_from_ref(value)
    }


@conferences.over('field_categories', '^65017')
@experiments.over('field_categories', '^65017')
@hep.over('field_categories', '^650[1_][_7]')
@hepnames.over('field_categories', '^65017')
@institutions.over('field_categories', '^65017')
@jobs.over('field_categories', '^65017')
@utils.for_each_value
def field_categories(self, key, value):
    """Field categories."""
    self.setdefault('field_categories', [])

    _terms = force_force_list(value.get('a'))

    if _terms:
        for _term in _terms:
            term = classify_field(_term)

            scheme = 'INSPIRE' if term else None

            _scheme = value.get('2')
            if isinstance(_scheme, (list, tuple)):
                _scheme = _scheme[0]

            source = value.get('9')
            if source:
                if 'automatically' in source:
                    source = 'INSPIRE'

            self['field_categories'].append({
                'source': source,
                '_scheme': _scheme,
                'scheme': scheme,
                '_term': _term,
                'term': term,
            })


@conferences.over('urls', '^8564')
@experiments.over('urls', '^8564')
@hep.over('urls', '^856.[10_28]')
@hepnames.over('urls', '^856.[10_28]')
@institutions.over('urls', '^856.[10_28]')
@jobs.over('urls', '^856.[10_28]')
@journals.over('urls', '^856.[10_28]')
@utils.for_each_value
def urls(self, key, value):
    """URL to external resource."""
    self.setdefault('urls', [])

    description = value.get('y')
    if isinstance(description, (list, tuple)):
        description = description[0]

    _urls = force_force_list(value.get('u'))

    if _urls:
        for _url in _urls:
            self['urls'].append({
                'description': description,
                'value': _url,
            })
