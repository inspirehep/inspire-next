# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016, 2017 CERN.
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

"""DoJSON common rules."""

from __future__ import absolute_import, division, print_function

import re
from datetime import datetime

from dojson import utils

from inspire_schemas.api import load_schema
from inspirehep.utils.helpers import force_force_list

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


IS_INTERNAL_UID = re.compile('^(inspire:uid:)?\d{5}$')
IS_ORCID = re.compile('^(orcid:)?\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$')


@hep.over('_fft', '^FFT..')
@utils.for_each_value
def _fft(self, key, value):
    def _get_creation_datetime(value):
        dt = datetime.strptime(value.get('s'), '%Y-%m-%d %H:%M:%S')
        return dt.isoformat()

    def _get_version(value):
        try:
            return int(force_single_element(value.get('v')))
        except ValueError:
            return None

    return {
        'creation_datetime': _get_creation_datetime(value),
        'description': value.get('d'),
        'filename': value.get('n'),
        'flags': force_force_list(value.get('o')),
        'format': value.get('f'),
        'path': value.get('a'),
        'status': value.get('z'),
        'type': value.get('t'),
        'version': _get_version(value),
    }


@hep2marc.over('FFT', '^_fft$')
@utils.for_each_value
def _fft2marc(self, key, value):
    def _get_s(value):
        if value.get('creation_datetime'):
            dt = datetime.strptime(value['creation_datetime'], '%Y-%m-%dT%H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')

    return {
        'a': value.get('path'),
        'd': value.get('description'),
        'f': value.get('format'),
        'n': value.get('filename'),
        'o': value.get('flags'),
        's': _get_s(value),
        't': value.get('type'),
        'v': value.get('version'),
        'z': value.get('status'),
    }


def self_url(index):
    def _self_url(self, key, value):
        self['control_number'] = int(value)
        return get_record_ref(value, index)
    return _self_url


institutions.over('self', '^001')(self_url('institutions'))
hep.over('self', '^001')(self_url('literature'))
conferences.over('self', '^001')(self_url('conferences'))
experiments.over('self', '^001')(self_url('experiments'))
journals.over('self', '^001')(self_url('journals'))
hepnames.over('self', '^001')(self_url('authors'))
jobs.over('self', '^001')(self_url('jobs'))


@hep2marc.over('001', '^control_number$')
@hepnames2marc.over('001', '^control_number$')
def control_number2marc(self, key, value):
    return value


@hep.over('acquisition_source', '^541..')
@hepnames.over('acquisition_source', '^541..')
def acquisition_source(self, key, value):
    internal_uid, orcid, source = None, None, None

    a_values = force_force_list(value.get('a'))
    for a_value in a_values:
        if IS_INTERNAL_UID.match(a_value):
            if a_value.startswith('inspire:uid:'):
                internal_uid = int(a_value[12:])
            else:
                internal_uid = int(a_value)
        elif IS_ORCID.match(a_value):
            if a_value.startswith('orcid:'):
                orcid = a_value[6:]
            else:
                orcid = a_value
        else:
            source = a_value

    c_value = force_single_element(value.get('c', ''))
    normalized_c_value = c_value.lower()

    if normalized_c_value == 'batchupload':
        method = 'batchuploader'
    elif normalized_c_value == 'submission':
        method = 'submitter'
    else:
        method = normalized_c_value

    return {
        'date': value.get('d'),
        'email': value.get('b'),
        'internal_uid': internal_uid,
        'method': method,
        'orcid': orcid,
        'source': source,
        'submission_number': value.get('e'),
    }


@hep2marc.over('541', '^acquisition_source$')
@hepnames2marc.over('541', '^acquisition_source$')
def acquisition_source2marc(self, key, value):
    orcid = value.get('orcid')
    source = value.get('source')

    a_value = 'orcid:' + orcid if orcid else source

    method = value.get('method')

    if method == 'batchuploader':
        c_value = 'batchupload'
    elif method == 'submitter':
        c_value = 'submission'
    else:
        c_value = method

    return {
        'a': a_value,
        'b': value.get('email'),
        'c': c_value,
        'd': value.get('date'),
        'e': value.get('submission_number'),
    }


@conferences.over('public_notes', '^500..')
@experiments.over('public_notes', '^500..')
@hep.over('public_notes', '^500..')
@hepnames.over('public_notes', '^500..')
@institutions.over('public_notes', '^500..')
@jobs.over('public_notes', '^500..')
@journals.over('public_notes', '^500..')
def public_notes_500(self, key, value):
    public_notes = self.get('public_notes', [])

    source = force_single_element(value.get('9', ''))
    for value in force_force_list(value):
        for public_note in force_force_list(value.get('a')):
            public_notes.append({
                'source': source,
                'value': public_note,
            })

    return public_notes


@hep2marc.over('500', '^public_notes$')
@hepnames2marc.over('500', '^public_notes$')
@utils.for_each_value
def public_notes2marc(self, key, value):
    return {
        '9': value.get('source'),
        'a': value.get('value'),
    }


@conferences.over('_private_notes', '^595..')
@experiments.over('_private_notes', '^595..')
@hepnames.over('_private_notes', '^595..')
@institutions.over('_private_notes', '^595..')
@jobs.over('_private_notes', '^595..')
@journals.over('_private_notes', '^595..')
@utils.for_each_value
def _private_notes_595(self, key, value):
    return {
        'source': value.get('9'),
        'value': value.get('a'),
    }


@hep2marc.over('595', '^_private_notes$')
@hepnames2marc.over('595', '^_private_notes$')
@utils.for_each_value
def _private_notes2marc(self, key, value):
    return {
        '9': value.get('source'),
        'a': value.get('value'),
    }


@conferences.over('inspire_categories', '^65017')
@experiments.over('inspire_categories', '^65017')
@hep.over('inspire_categories', '^65017')
@institutions.over('inspire_categories', '^65017')
@jobs.over('inspire_categories', '^65017')
def inspire_categories(self, key, value):
    schema = load_schema('elements/inspire_field')
    valid_sources = schema['properties']['source']['enum']

    inspire_categories = self.get('inspire_categories', [])

    scheme = force_single_element(value.get('2'))
    if scheme == 'arXiv':          # XXX: we skip arXiv categories here because
        return inspire_categories  # we're going to add them later in a filter.

    source = force_single_element(value.get('9'))
    if source not in valid_sources:
        if source == 'automatically added based on DCC, PPF, DK':
            source = 'curator'
        elif source == 'submitter':
            source = 'user'
        else:
            source = 'undefined'

    terms = force_force_list(value.get('a'))
    for _term in terms:
        term = classify_field(_term)
        if term:
            inspire_categories.append({
                'term': term,
                'source': source,
            })

    return inspire_categories


@hep2marc.over('65017', '^inspire_categories$')
@utils.for_each_value
def inspire_categories2marc(self, key, value):
    return {
        '2': 'INSPIRE',
        '9': value.get('source'),
        'a': value.get('term'),
    }


@conferences.over('_private_notes', '^667..')
@experiments.over('_private_notes', '^667..')
@hep.over('_private_notes', '^667..')
@institutions.over('_private_notes', '^667..')
@jobs.over('_private_notes', '^667..')
@journals.over('_private_notes', '^667..')
@utils.for_each_value
def _private_notes_667(self, key, value):
    return {
        'source': value.get('9'),
        'value': value.get('a'),
    }


@conferences.over('public_notes', '^680..')
@experiments.over('public_notes', '^680..')
@institutions.over('public_notes', '^680..')
@jobs.over('public_notes', '^680..')
@journals.over('public_notes', '^680..')
@utils.for_each_value
def public_notes_680(self, key, value):
    return {
        'source': value.get('9'),
        'value': value.get('i'),
    }


@conferences.over('urls', '^8564.')
@experiments.over('urls', '^8564.')
@hep.over('urls', '^8564.')
@hepnames.over('urls', '^8564.')
@institutions.over('urls', '^8564.')
@jobs.over('urls', '^8564.')
@journals.over('urls', '^8564.')
def urls(self, key, value):
    urls = self.get('urls', [])

    description = force_single_element(value.get('y'))
    for url in force_force_list(value.get('u')):
        urls.append({
            'description': description,
            'value': url,
        })

    return urls


@conferences.over('legacy_creation_date', '^961..')
@experiments.over('legacy_creation_date', '^961..')
@hep.over('legacy_creation_date', '^961..')
@hepnames.over('legacy_creation_date', '^961..')
@institutions.over('legacy_creation_date', '^961..')
@jobs.over('legacy_creation_date', '^961..')
@journals.over('legacy_creation_date', '^961..')
def legacy_creation_date(self, key, value):
    if 'legacy_creation_date' in self:
        return self['legacy_creation_date']

    return value.get('x')


@hep2marc.over('961', '^legacy_creation_date$')
@hepnames2marc.over('961', '^legacy_creation_date$')
def legacy_creation_date2marc(self, key, value):
    return {'x': value}


@conferences.over('external_system_identifiers', '^970..')
@experiments.over('external_system_identifiers', '^970..')
@hep.over('external_system_identifiers', '^970..')
@institutions.over('external_system_identifiers', '^970..')
@journals.over('external_system_identifiers', '^970..')
@jobs.over('external_system_identifiers', '^970..')
def external_system_identifiers(self, key, value):
    """Populate the ``external_system_identifiers`` key.

    Also populates the ``new_record`` key through side effects.
    """
    external_system_identifiers = self.get('external_system_identifiers', [])
    new_record = self.get('new_record', {})

    for value in force_force_list(value):
        for id_ in force_force_list(value.get('a')):
            external_system_identifiers.append({
                'schema': 'SPIRES',
                'value': id_,
            })

        new_recid = force_single_element(value.get('d', ''))
        if new_recid:
            new_record = get_record_ref(new_recid)

    self['new_record'] = new_record
    return external_system_identifiers


@hep2marc.over('970', '^new_record$')
@hepnames2marc.over('970', '^new_record$')
def new_record2marc(self, key, value):
    return {'d': get_recid_from_ref(value)}


@conferences.over('deleted', '^980..')
@institutions.over('deleted', '^980..')
@experiments.over('deleted', '^980..')
@jobs.over('deleted', '^980..')
@journals.over('deleted', '^980..')
def deleted(self, key, value):
    return value.get('c', '').upper() == 'DELETED'


@conferences.over('deleted_records', '^981..')
@experiments.over('deleted_records', '^981..')
@hep.over('deleted_records', '^981..')
@hepnames.over('deleted_records', '^981..')
@institutions.over('deleted_records', '^981..')
@jobs.over('deleted_records', '^981..')
@journals.over('deleted_records', '^981..')
@utils.for_each_value
def deleted_records(self, key, value):
    return get_record_ref(value.get('a'))


@hep2marc.over('981', 'deleted_records')
@hepnames2marc.over('981', 'deleted_records')
@utils.for_each_value
def deleted_records2marc(self, key, value):
    return {'a': get_recid_from_ref(value)}
