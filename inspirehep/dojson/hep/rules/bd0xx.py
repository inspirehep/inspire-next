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

"""DoJSON rules for MARC fields in 0xx."""

from __future__ import absolute_import, division, print_function

import re

import pycountry

from dojson import utils
from idutils import is_doi, is_handle, normalize_doi

from inspire_schemas.utils import load_schema
from inspirehep.utils.helpers import force_force_list

from ..model import hep, hep2marc
from ...utils import force_single_element


RE_LANGUAGE = re.compile('\/| or | and |,|=|\s+')


@hep.over('isbns', '^020..')
@utils.for_each_value
def isbns(self, key, value):
    def _get_medium(value):
        def _normalize(medium):
            schema = load_schema('hep')
            valid_media = schema['properties']['isbns']['items']['properties']['medium']['enum']

            medium = medium.lower().replace('-', '').replace(' ', '')
            if medium in valid_media:
                return medium
            elif medium == 'ebook':
                return 'online'
            elif medium == 'paperback':
                return 'softcover'

            return ''

        medium = force_single_element(value.get('b', ''))
        normalized_medium = _normalize(medium)

        return normalized_medium

    def _get_isbn(value):
        def _normalize(isbn):
            return isbn.upper().replace('-', '')

        isbn = force_single_element(value.get('a', ''))
        normalized_isbn = _normalize(isbn)

        return normalized_isbn

    return {
        'medium': _get_medium(value),
        'value': _get_isbn(value),
    }


@hep2marc.over('020', 'isbns')
@utils.for_each_value
def isbns2marc(self, key, value):
    return {
        'a': value.get('value'),
        'b': value.get('medium'),
    }


@hep.over('dois', '^0247.')
def dois(self, key, value):
    """Populate the ``dois`` key.

    Also populates the ``persistent_identifiers`` key through side effects.
    """
    def _get_first_non_curator_source(sources):
        sources_without_curator = [el for el in sources if el.upper() != 'CURATOR']
        return force_single_element(sources_without_curator)

    def _is_doi(id_, type_):
        return (not type_ or type_.upper() == 'DOI') and is_doi(id_)

    def _is_handle(id_, type_):
        return (not type_ or type_.upper() == 'HDL') and is_handle(id_)

    dois = self.get('dois', [])
    persistent_identifiers = self.get('persistent_identifiers', [])

    values = force_force_list(value)
    for value in values:
        id_ = force_single_element(value.get('a', ''))
        material = force_single_element(value.get('q', ''))
        schema = force_single_element(value.get('2', ''))

        sources = force_force_list(value.get('9'))
        source = _get_first_non_curator_source(sources)

        if _is_doi(id_, schema):
            dois.append({
                'material': material,
                'source': source,
                'value': normalize_doi(id_),
            })
        else:
            schema = 'HDL' if _is_handle(id_, schema) else schema
            persistent_identifiers.append({
                'material': material,
                'schema': schema,
                'source': source,
                'value': id_,
            })

    self['persistent_identifiers'] = persistent_identifiers
    return dois


@hep2marc.over('0247', '^dois$')
@utils.for_each_value
def dois2marc(self, key, value):
    return {
        '2': 'DOI',
        '9': value.get('source'),
        'a': value.get('value'),
        'q': value.get('material'),
    }


@hep2marc.over('0247', '^persistent_identifiers$')
@utils.for_each_value
def persistent_identifiers2marc(self, key, value):
    return {
        '2': value.get('schema'),
        '9': value.get('source'),
        'a': value.get('value'),
        'q': value.get('material'),
    }


@hep.over('texkeys', '^035..')
def texkeys(self, key, value):
    """Populate the ``texkeys`` key.

    Also populates the ``external_system_identifiers`` key through side effects.
    """
    def _is_arxiv(id_, schema):
        return id_ and schema in ('arXiv',)

    def _is_cernkey(id_, schema):
        return id_ and schema in ('CERNKEY',)

    def _is_desy(id_, schema):
        return id_ and schema in ('DESY',)

    def _is_texkey(id_, schema):
        return id_ and schema in ('INSPIRETeX', 'SPIRESTeX')

    texkeys = self.get('texkeys', [])
    external_system_identifiers = self.get('external_system_identifiers', [])

    values = force_force_list(value)
    for value in values:
        id_ = force_single_element(value.get('a', ''))
        other_id = force_single_element(value.get('z', ''))
        schema = force_single_element(value.get('9', ''))

        if _is_texkey(id_, schema):
            texkeys.insert(0, id_)
        elif _is_texkey(other_id, schema):
            texkeys.append(other_id)
        elif _is_cernkey(other_id, schema):
            external_system_identifiers.append({
                'schema': 'CERNKEY',
                'value': other_id,
            })
        elif _is_desy(other_id, schema):
            external_system_identifiers.append({
                'schema': 'DESY',
                'value': other_id,
            })
        elif _is_arxiv(id_, schema) or _is_arxiv(other_id, schema):
            continue  # XXX: ignored.
        else:
            external_system_identifiers.append({
                'schema': schema,
                'value': id_,
            })

    self['external_system_identifiers'] = external_system_identifiers
    return texkeys


@hep2marc.over('035', '^texkeys$')
def texkeys2marc(self, key, value):
    result = []

    values = force_force_list(value)
    if values:
        value = values[0]
        result.append({
            '9': 'INSPIRETeX',
            'a': value,
        })

        for value in values[1:]:
            result.append({
                '9': 'INSPIRETeX',
                'z': value,
            })

    return result


@hep2marc.over('035', '^external_system_identifiers$')
def external_system_identifiers2marc(self, key, value):
    """Populate the ``035`` MARC field.

    Also populates the ``970`` MARC field through side effects.
    """
    def _is_scheme_cernkey(id_, schema):
        return schema == 'CERNKEY'

    def _is_scheme_spires(id_, schema):
        return schema == 'SPIRES'

    result_035 = self.get('035', [])
    result_970 = self.get('970', [])

    values = force_force_list(value)
    for value in values:
        id_ = value.get('value')
        schema = value.get('schema')

        if _is_scheme_spires(id_, schema):
            result_970.append({
                'a': id_,
            })
        elif _is_scheme_cernkey(id_, schema):
            result_035.append({
                '9': 'CERNKEY',
                'z': id_,
            })
        else:
            result_035.append({
                '9': schema,
                'a': id_,
            })

    self['970'] = result_970
    return result_035


@hep.over('arxiv_eprints', '^037..')
def arxiv_eprints(self, key, value):
    """Populate the ``arxiv_eprints`` key.

    Also populates the ``report_numbers`` key through side effects.
    """
    def _get_clean_arxiv_eprint(id_):
        return id_.split(':')[-1]

    def _is_arxiv_eprint(id_, source):
        return source == 'arXiv'

    def _is_hidden_report_number(other_id, source):
        return other_id

    arxiv_eprints = self.get('arxiv_eprints', [])
    report_numbers = self.get('report_numbers', [])

    values = force_force_list(value)
    for value in values:
        id_ = force_single_element(value.get('a', ''))
        other_id = force_single_element(value.get('z', ''))
        categories = force_force_list(value.get('c'))
        source = force_single_element(value.get('9', ''))

        if _is_arxiv_eprint(id_, source):
            arxiv_eprints.append({
                'categories': categories,
                'value': _get_clean_arxiv_eprint(id_),
            })
        elif _is_hidden_report_number(other_id, source):
            report_numbers.append({
                'hidden': True,
                'source': source,
                'value': other_id,
            })
        else:
            report_numbers.append({
                'source': source,
                'value': id_,
            })

    self['report_numbers'] = report_numbers
    return arxiv_eprints


@hep2marc.over('037', '^arxiv_eprints$')
def arxiv_eprints2marc(self, key, value):
    """Populate the ``037`` MARC field.

    Also populates the ``035`` and the ``65017`` MARC fields through side effects.
    """
    result_037 = self.get('037', [])
    result_035 = self.get('035', [])
    result_65017 = self.get('65017', [])

    values = force_force_list(value)
    for value in values:
        result_037.append({
            '9': 'arXiv',
            'a': 'arXiv:' + value.get('value'),
            'c': force_single_element(value.get('categories')),
        })

        result_035.append({
            '9': 'arXiv',
            'a': 'oai:arXiv.org:' + value.get('value'),
        })

        categories = force_force_list(value.get('categories'))
        for category in categories:
            result_65017.append({
                '2': 'arXiv',
                'a': category,
            })

    self['65017'] = result_65017
    self['035'] = result_035
    return result_037


@hep2marc.over('037', '^report_numbers$')
@utils.for_each_value
def report_numbers2marc(self, key, value):
    if value.get('hidden'):
        return {
            '9': value.get('source'),
            'z': value.get('value'),
        }

    return {
        '9': value.get('source'),
        'a': value.get('value'),
    }


@hep.over('languages', '^041..')
def languages(self, key, value):
    languages = self.get('languages', [])

    values = force_force_list(value.get('a'))
    for value in values:
        for language in RE_LANGUAGE.split(value):
            try:
                name = language.strip().capitalize()
                languages.append(pycountry.languages.get(name=name).alpha_2)
            except KeyError:
                pass

    return languages


@hep2marc.over('041', '^languages$')
@utils.for_each_value
def languages2marc(self, key, value):
    return {'a': pycountry.languages.get(alpha_2=value).name.lower()}
