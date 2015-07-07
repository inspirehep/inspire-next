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


@inspiremarc.over('added_entry_personal_name', '^700[103_][_2]')
@utils.for_each_value
@utils.filter_values
def added_entry_personal_name(self, key, value):
    """Added Entry-Personal Name."""
    indicator_map1 = {"0": "Forename", "1": "Surname", "3": "Family name"}
    indicator_map2 = {"#": "No information provided", "2": "Analytical entry"}
    return {
        'authority_record_control_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'personal_name': utils.force_list(
            value.get('a')
        ),
        'titles_and_other_words_associated_with_a_name': value.get('c'),
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
        'relationship_information': value.get('i'),
        'medium': utils.force_list(
            value.get('h')
        ),
        'form_subheading': value.get('k'),
        'attribution_qualifier': value.get('j'),
        'medium_of_performance_for_music': value.get('m'),
        'language_of_a_work': utils.force_list(
            value.get('l')
        ),
        'arranged_statement_for_music': utils.force_list(
            value.get('o')
        ),
        'number_of_part_section_of_a_work': value.get('n'),
        'fuller_form_of_name': utils.force_list(
            value.get('q')
        ),
        'name_of_part_section_of_a_work': value.get('p'),
        'version': utils.force_list(
            value.get('s')
        ),
        'key_for_music': utils.force_list(
            value.get('r')
        ),
        'affiliation': utils.force_list(
            value.get('u')
        ),
        'title_of_a_work': utils.force_list(
            value.get('t')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'type_of_personal_name_entry_element': indicator_map1.get(key[3]),
        'type_of_added_entry': indicator_map2.get(key[4]),
    }


@inspiremarc.over('added_entry_corporate_name', '^710[10_2][_2]')
@utils.for_each_value
@utils.filter_values
def added_entry_corporate_name(self, key, value):
    """Added Entry-Corporate Name."""
    indicator_map1 = {
        "0": "Inverted name", "1": "Jurisdiction name", "2": "Name in direct order"}
    indicator_map2 = {"#": "No information provided", "2": "Analytical entry"}
    return {
        'authority_record_control_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'corporate_name_or_jurisdiction_name_as_entry_element': utils.force_list(
            value.get('a')
        ),
        'location_of_meeting': utils.force_list(
            value.get('c')
        ),
        'subordinate_unit': value.get('b'),
        'relator_term': value.get('e'),
        'date_of_meeting_or_treaty_signing': value.get('d'),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_of_a_work': utils.force_list(
            value.get('f')
        ),
        'relationship_information': value.get('i'),
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
        'number_of_part_section_meeting': value.get('n'),
        'name_of_part_section_of_a_work': value.get('p'),
        'version': utils.force_list(
            value.get('s')
        ),
        'key_for_music': utils.force_list(
            value.get('r')
        ),
        'affiliation': utils.force_list(
            value.get('u')
        ),
        'title_of_a_work': utils.force_list(
            value.get('t')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'type_of_corporate_name_entry_element': indicator_map1.get(key[3]),
        'type_of_added_entry': indicator_map2.get(key[4]),
    }


@inspiremarc.over('added_entry_meeting_name', '^711[10_2][_2]')
@utils.for_each_value
@utils.filter_values
def added_entry_meeting_name(self, key, value):
    """Added Entry-Meeting Name."""
    indicator_map1 = {
        "0": "Inverted name", "1": "Jurisdiction name", "2": "Name in direct order"}
    indicator_map2 = {"#": "No information provided", "2": "Analytical entry"}
    return {
        'authority_record_control_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'meeting_name_or_jurisdiction_name_as_entry_element': utils.force_list(
            value.get('a')
        ),
        'location_of_meeting': utils.force_list(
            value.get('c')
        ),
        'subordinate_unit': value.get('e'),
        'date_of_meeting': utils.force_list(
            value.get('d')
        ),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_of_a_work': utils.force_list(
            value.get('f')
        ),
        'relationship_information': value.get('i'),
        'medium': utils.force_list(
            value.get('h')
        ),
        'form_subheading': value.get('k'),
        'relator_term': value.get('j'),
        'language_of_a_work': utils.force_list(
            value.get('l')
        ),
        'number_of_part_section_meeting': value.get('n'),
        'name_of_meeting_following_jurisdiction_name_entry_element': utils.force_list(
            value.get('q')
        ),
        'name_of_part_section_of_a_work': value.get('p'),
        'version': utils.force_list(
            value.get('s')
        ),
        'affiliation': utils.force_list(
            value.get('u')
        ),
        'title_of_a_work': utils.force_list(
            value.get('t')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'type_of_meeting_name_entry_element': indicator_map1.get(key[3]),
        'type_of_added_entry': indicator_map2.get(key[4]),
    }


@inspiremarc.over('added_entry_uncontrolled_name', '^720[1_2].')
@utils.for_each_value
@utils.filter_values
def added_entry_uncontrolled_name(self, key, value):
    """Added Entry-Uncontrolled Name."""
    indicator_map1 = {"#": "Not specified", "1": "Personal", "2": "Other"}
    return {
        'name': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'relator_term': value.get('e'),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'type_of_name': indicator_map1.get(key[3]),
    }


@inspiremarc.over('added_entry_uniform_title', '^730.[_2]')
@utils.for_each_value
@utils.filter_values
def added_entry_uniform_title(self, key, value):
    """Added Entry-Uniform Title."""
    indicator_map2 = {"#": "No information provided", "2": "Analytical entry"}
    return {
        'uniform_title': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'name_of_part_section_of_a_work': value.get('p'),
        'date_of_treaty_signing': value.get('d'),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_of_a_work': utils.force_list(
            value.get('f')
        ),
        'relationship_information': value.get('i'),
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
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'key_for_music': utils.force_list(
            value.get('r')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'title_of_a_work': utils.force_list(
            value.get('t')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'version': utils.force_list(
            value.get('s')
        ),
        'type_of_added_entry': indicator_map2.get(key[4]),
    }


@inspiremarc.over(
    'added_entry_uncontrolled_related_analytical_title', '^740[0_][_2]')
@utils.for_each_value
@utils.filter_values
def added_entry_uncontrolled_related_analytical_title(self, key, value):
    """Added Entry-Uncontrolled Related/Analytical Title."""
    indicator_map1 = {"0": "No nonfiling characters"}
    indicator_map2 = {"#": "No information provided", "2": "Analytical entry"}
    return {
        'uncontrolled_related_analytical_title': utils.force_list(
            value.get('a')
        ),
        'medium': utils.force_list(
            value.get('h')
        ),
        'number_of_part_section_of_a_work': value.get('n'),
        'name_of_part_section_of_a_work': value.get('p'),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'nonfiling_characters': indicator_map1.get(key[3]),
        'type_of_added_entry': indicator_map2.get(key[4]),
    }


@inspiremarc.over('added_entry_geographic_name', '^751..')
@utils.for_each_value
@utils.filter_values
def added_entry_geographic_name(self, key, value):
    """Added Entry-Geographic Name."""
    return {
        'geographic_name': utils.force_list(
            value.get('a')
        ),
        'relator_term': value.get('e'),
        'authority_record_control_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_heading_or_term': utils.force_list(
            value.get('2')
        ),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('added_entry_hierarchical_place_name', '^752..')
@utils.for_each_value
@utils.filter_values
def added_entry_hierarchical_place_name(self, key, value):
    """Added Entry-Hierarchical Place Name."""
    return {
        'country_or_larger_entity': value.get('a'),
        'intermediate_political_jurisdiction': value.get('c'),
        'first_order_political_jurisdiction': utils.force_list(
            value.get('b')
        ),
        'city': utils.force_list(
            value.get('d')
        ),
        'other_nonjurisdictional_geographic_region_and_feature': value.get('g'),
        'city_subsection': value.get('f'),
        'extraterrestrial_area': value.get('h'),
        'authority_record_control_number': value.get('0'),
        'source_of_heading_or_term': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('system_details_access_to_computer_files', '^753..')
@utils.for_each_value
@utils.filter_values
def system_details_access_to_computer_files(self, key, value):
    """System Details Access to Computer Files."""
    return {
        'make_and_model_of_machine': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'operating_system': utils.force_list(
            value.get('c')
        ),
        'programming_language': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('added_entry_taxonomic_identification', '^754..')
@utils.for_each_value
@utils.filter_values
def added_entry_taxonomic_identification(self, key, value):
    """Added Entry-Taxonomic Identification."""
    return {
        'taxonomic_name': value.get('a'),
        'non_public_note': value.get('x'),
        'taxonomic_category': value.get('c'),
        'common_or_alternative_name': value.get('d'),
        'authority_record_control_number': value.get('0'),
        'source_of_taxonomic_identification': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'public_note': value.get('z'),
    }
