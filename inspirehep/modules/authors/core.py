# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Core functions for authors."""

from __future__ import absolute_import, division, print_function


def convert_for_form(author_record):
    """Convert author data model form field names.

    TODO: This might be better in a different file and as a dojson conversion.
    """
    record_keys = author_record.keys()

    keys_to_setters_mapping = {
        'advisors': _set_advisors,
        'arxiv_categories': _set_research_field,
        'ids': _set_ids_schema_based_fields,
        'name': _set_name_based_fields,
        'native_name': _set_native_name,
        'positions': _set_institution_history_and_public_emails,
        'urls': _set_websites_based_fields,
    }

    for key in record_keys:
        if key in keys_to_setters_mapping:
            keys_to_setters_mapping[key](author_record)


def _set_advisors(author_record):
    advisors = author_record['advisors']
    author_record['advisors'] = []
    for advisor in advisors:
        adv = dict(degree_type=advisor.get('degree_type', ''), name=advisor.get('name', ''))
        author_record['advisors'].append(adv)


def _set_ids_schema_based_fields(author_record):
    schema_to_field_mappings = {
        'ORCID': 'orcid',
        'INSPIRE BAI': 'bai',
        'INSPIRE ID': 'inspireid',
    }

    for current_id in author_record['ids']:
        try:
            field = schema_to_field_mappings[current_id['schema']]
            author_record[field] = current_id['value']
        except KeyError:
            # Protect against cases when there is no value in metadata
            pass


def _set_institution_history_and_public_emails(author_record):
    author_record['institution_history'] = []
    author_record['public_emails'] = []

    for position in author_record['positions']:
        if not any(
                [
                    key in position
                    for key in ('institution', '_rank', 'start_year', 'end_year')
                ]
        ):
            if 'emails' in position:
                for email in position['emails']:
                    author_record['public_emails'].append(
                        {
                            'email': email,
                            'original_email': email
                        }
                    )
            continue

        pos = dict(name=position.get('institution', {}).get('name'))

        rank = position.get('_rank', '')
        if rank:
            pos['rank'] = rank

        _set_int_or_skip(pos, 'start_year', position.get('start_date', ''))
        _set_int_or_skip(pos, 'end_year', position.get('end_date', ''))
        pos['current'] = True if position.get('current') else False
        pos['old_emails'] = position.get('old_emails', [])

        if position.get('emails'):
            pos['emails'] = position['emails']
            for email in position['emails']:
                author_record['public_emails'].append(
                    {
                        'email': email,
                        'original_email': email
                    }
                )
        author_record['institution_history'].append(pos)
    author_record['institution_history'].reverse()


def _set_int_or_skip(provided_dict, key, provided_int):
    try:
        provided_dict[key] = int(provided_int)
    except ValueError:
        pass


def _set_name_based_fields(author_record):
    author_record['full_name'] = author_record['name'].get('value')

    try:
        author_name = author_record['name'].get('value')
        author_record['given_names'] = author_name.split(',')[1].strip() or ''
    except IndexError:
        author_record['given_names'] = ''

    author_record['family_name'] = author_record['name'].get('value').split(',')[0].strip()
    author_record['display_name'] = author_record["name"].get('preferred_name')


def _set_native_name(author_record):
    author_record['native_name'] = author_record['native_name'][0]


def _set_research_field(author_record):
    author_record['research_field'] = author_record['arxiv_categories']


def _set_websites_based_fields(author_record):
    author_record['websites'] = []

    description_to_field_mappings = {
        'twitter': 'twitter_url',
        'blog': 'blog_url',
        'linkedin': 'linkedin_url',
    }

    for url in author_record['urls']:
        if not url.get('description'):
            author_record['websites'].append({'webpage': url['value']})
        else:
            try:
                field = description_to_field_mappings[url['description'].lower()]
                author_record[field] = url['value']
            except KeyError:
                # Protect against cases when there is no value in metadata
                pass
    del author_record['urls']
