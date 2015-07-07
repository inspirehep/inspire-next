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


@inspiremarc.over('main_entry_personal_name', '^100[103_].')
@utils.filter_values
def main_entry_personal_name(self, key, value):
    """Main Entry-Personal Name."""
    indicator_map1 = {"0": "Forename", "1": "Surname", "3": "Family name"}
    return {
        'personal_name': utils.force_list(
            value.get('a')
        ),
        'titles_and_words_associated_with_a_name': value.get('c'),
        'numeration': utils.force_list(
            value.get('b')
        ),
        'relator_term': value.get('e'),
        'dates_associated_with_a_name': utils.force_list(
            value.get('d')
        ),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_of_a_work': utils.force_list(
            value.get('f')
        ),
        'form_subheading': value.get('k'),
        'attribution_qualifier': value.get('j'),
        'language_of_a_work': utils.force_list(
            value.get('l')
        ),
        'name_of_part_section_of_a_work': value.get('p'),
        'number_of_part_section_of_a_work': value.get('n'),
        'fuller_form_of_name': utils.force_list(
            value.get('q')
        ),
        'authority_record_control_number': value.get('0'),
        'affiliation': utils.force_list(
            value.get('u')
        ),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title_of_a_work': utils.force_list(
            value.get('t')
        ),
        'type_of_personal_name_entry_element': indicator_map1.get(key[3]),
    }


@inspiremarc.over('main_entry_corporate_name', '^110[10_2].')
@utils.filter_values
def main_entry_corporate_name(self, key, value):
    """Main Entry-Corporate Name."""
    indicator_map1 = {
        "0": "Inverted name",
        "1": "Jurisdiction name",
        "2": "Name in direct order"}
    return {
        'corporate_name_or_jurisdiction_name_as_entry_element': utils.force_list(
            value.get('a')),
        'location_of_meeting': utils.force_list(
            value.get('c')),
        'subordinate_unit': value.get('b'),
        'relator_term': value.get('e'),
        'date_of_meeting_or_treaty_signing': value.get('d'),
        'miscellaneous_information': utils.force_list(
            value.get('g')),
        'date_of_a_work': utils.force_list(
            value.get('f')),
        'form_subheading': value.get('k'),
        'language_of_a_work': utils.force_list(
            value.get('l')),
        'name_of_part_section_of_a_work': value.get('p'),
        'number_of_part_section_meeting': value.get('n'),
        'authority_record_control_number': value.get('0'),
        'affiliation': utils.force_list(
            value.get('u')),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')),
        'field_link_and_sequence_number_r': value.get('8'),
        'title_of_a_work': utils.force_list(
            value.get('t')),
        'type_of_corporate_name_entry_element': indicator_map1.get(
            key[3]),
    }


@inspiremarc.over('main_entry_meeting_name', '^111[10_2].')
@utils.filter_values
def main_entry_meeting_name(self, key, value):
    """Main Entry-Meeting Name."""
    indicator_map1 = {
        "0": "Inverted name",
        "1": "Jurisdiction name",
        "2": "Name in direct order"}
    return {
        'meeting_name_or_jurisdiction_name_as_entry_element': utils.force_list(
            value.get('a')),
        'location_of_meeting': utils.force_list(
            value.get('c')),
        'subordinate_unit': value.get('e'),
        'date_of_meeting': utils.force_list(
            value.get('d')),
        'miscellaneous_information': utils.force_list(
            value.get('g')),
        'date_of_a_work': utils.force_list(
            value.get('f')),
        'form_subheading': value.get('k'),
        'relator_term': value.get('j'),
        'language_of_a_work': utils.force_list(
            value.get('l')),
        'name_of_part_section_of_a_work': value.get('p'),
        'number_of_part_section_meeting': value.get('n'),
        'name_of_meeting_following_jurisdiction_name_entry_element': utils.force_list(
            value.get('q')),
        'authority_record_control_number': value.get('0'),
        'affiliation': utils.force_list(
            value.get('u')),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')),
        'field_link_and_sequence_number': value.get('8'),
        'title_of_a_work': utils.force_list(
            value.get('t')),
        'type_of_meeting_name_entry_element': indicator_map1.get(
            key[3]),
    }


@inspiremarc.over('main_entry_uniform_title', '^130..')
@utils.filter_values
def main_entry_uniform_title(self, key, value):
    """Main Entry-Uniform Title."""
    return {
        'uniform_title': utils.force_list(
            value.get('a')
        ),
        'name_of_part_section_of_a_work': value.get('p'),
        'date_of_treaty_signing': value.get('d'),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_of_a_work': utils.force_list(
            value.get('f')
        ),
        'medium': utils.force_list(
            value.get('h')
        ),
        'form_subheading': value.get('k'),
        'medium_of_performance_for_music': value.get('m'),
        'language_of_a_work': utils.force_list(
            value.get('l')
        ),
        'arranged_statement_for_music': utils.force_list(
            value.get('o')
        ),
        'number_of_part_section_of_a_work': value.get('n'),
        'authority_record_control_number': value.get('0'),
        'version': utils.force_list(
            value.get('s')
        ),
        'key_for_music': utils.force_list(
            value.get('r')
        ),
        'title_of_a_work': utils.force_list(
            value.get('t')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }
