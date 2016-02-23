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

from inspirehep.dojson import utils as inspire_dojson_utils
from inspirehep.dojson.utils import strip_empty_values

from ..hep.model import hep, hep2marc
from ..conferences.model import conferences
from ..institutions.model import institutions
from ..experiments.model import experiments
from ..journals.model import journals
from ..hepnames.model import hepnames, hepnames2marc
from ..jobs.model import jobs


@institutions.over('control_number', '^001')
@hep.over('control_number', '^001')
@conferences.over('control_number', '^001')
@experiments.over('control_number', '^001')
@journals.over('control_number', '^001')
@hepnames.over('control_number', '^001')
@jobs.over('control_number', '^001')
def control_number(self, key, value):
    """Record Identifier."""
    return value


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


@hep.over('oai_pmh', '^909CO')
@conferences.over('oai_pmh', '^909CO')
@institutions.over('oai_pmh', '^909CO')
@experiments.over('oai_pmh', '^909CO')
@journals.over('oai_pmh', '^909CO')
@hepnames.over('oai_pmh', '^909CO')
@jobs.over('oai_pmh', '^909CO')
@utils.for_each_value
@utils.filter_values
def oai_pmh(self, key, value):
    """Local OAI-PMH record information."""
    return {
        'id': value.get('o'),
        'set': value.get('p'),
        'previous_set': value.get('q'),
    }


@hep2marc.over('909CO', 'oai_pmh')
@hepnames2marc.over('909CO', 'oai_pmh')
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
    value = utils.force_list(value)
    sysnos = []
    new_recid = None
    for val in value:
        if 'a' in val:
            # Only append if there is something
            sysnos.append(val.get('a'))
        elif 'd' in val:
            new_recid = val.get('d')
    if new_recid is not None:
        self['new_recid'] = new_recid
    return sysnos or None


@hep2marc.over('970', '(spires_sysnos|new_recid)')
@hepnames2marc.over('970', '(spires_sysnos|new_recid)')
def spires_sysnos2marc(self, key, value):
    """970 SPIRES number and new recid."""
    value = utils.force_list(value)
    existing_values = self.get('970', [])

    if key == 'spires_sysnos':
        existing_values.extend(
            [{'a': val} for val in value if val]
        )
    elif key == 'new_recid':
        existing_values.extend(
            [{'d': val} for val in value if val]
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
    value = utils.force_list(value)

    def get_value(value):
        primary = ''
        if isinstance(value.get('a'), list):
            primary = value.get('a')[0]
        else:
            primary = value.get('a')
        return {
            'primary': primary,
            'secondary': value.get('b'),
            'deleted': value.get('c'),
        }

    collections = self.get('collections', [])

    for val in value:
        collections.append(get_value(val))

    contains_list = False
    for element in collections:
        for k, v in enumerate(element):
            if isinstance(element[v], list):
                contains_list = True
                break
    if contains_list:
        return strip_empty_values(collections)
    else:
        return inspire_dojson_utils.remove_duplicates_from_list_of_dicts(
            collections)


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


@hep.over('deleted_recids', '^981..')
@conferences.over('deleted_recids', '^981..')
@institutions.over('deleted_recids', '^981..')
@experiments.over('deleted_recids', '^981..')
@journals.over('deleted_recids', '^981..')
@hepnames.over('deleted_recids', '^981..')
@jobs.over('deleted_recids', '^981..')
@utils.for_each_value
@utils.ignore_value
def deleted_recids(self, key, value):
    """Recid of deleted record this record is master for."""
    return value.get('a')


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


@hep2marc.over('981', 'deleted_recids')
@hepnames2marc.over('981', 'deleted_recids')
@utils.for_each_value
@utils.filter_values
def deleted_recids2marc(self, key, value):
    """Deleted recids."""
    return {
        'a': value
    }
