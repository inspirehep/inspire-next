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


@inspiremarc.over('main_series_entry', '^760[10_][8_]')
@utils.for_each_value
@utils.filter_values
def main_series_entry(self, key, value):
    """Main Series Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {"#": "Main series", "8": "No display constant generated"}
    return {
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'record_control_number': value.get('w'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title': utils.force_list(
            value.get('t')
        ),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('subseries_entry', '^762[10_][8_]')
@utils.for_each_value
@utils.filter_values
def subseries_entry(self, key, value):
    """Subseries Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Has subseries", "8": "No display constant generated"}
    return {
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'record_control_number': value.get('w'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title': utils.force_list(
            value.get('t')
        ),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('original_language_entry', '^765[10_][8_]')
@utils.for_each_value
@utils.filter_values
def original_language_entry(self, key, value):
    """Original Language Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Translation of", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('translation_entry', '^767[10_][8_]')
@utils.for_each_value
@utils.filter_values
def translation_entry(self, key, value):
    """Translation Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Translated as", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('supplement_special_issue_entry', '^770[10_][8_]')
@utils.for_each_value
@utils.filter_values
def supplement_special_issue_entry(self, key, value):
    """Supplement/Special Issue Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Has supplement", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('supplement_parent_entry', '^772[10_][0_8]')
@utils.for_each_value
@utils.filter_values
def supplement_parent_entry(self, key, value):
    """Supplement Parent Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Supplement to",
        "0": "Parent",
        "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('host_item_entry', '^773[10_][8_]')
@utils.for_each_value
@utils.filter_values
def host_item_entry(self, key, value):
    """Host Item Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {"#": "In", "8": "No display constant generated"}
    return {
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'enumeration_and_first_page': utils.force_list(
            value.get('q')
        ),
        'abbreviated_title': utils.force_list(
            value.get('p')
        ),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('constituent_unit_entry', '^774[10_][8_]')
@utils.for_each_value
@utils.filter_values
def constituent_unit_entry(self, key, value):
    """Constituent Unit Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Constituent unit", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('other_edition_entry', '^775[10_][8_]')
@utils.for_each_value
@utils.filter_values
def other_edition_entry(self, key, value):
    """Other Edition Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Other edition available", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'language_code': utils.force_list(
            value.get('e')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'country_code': utils.force_list(
            value.get('f')
        ),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('additional_physical_form_entry', '^776[10_][8_]')
@utils.for_each_value
@utils.filter_values
def additional_physical_form_entry(self, key, value):
    """Additional Physical Form Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Available in another form", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('issued_with_entry', '^777[10_][8_]')
@utils.for_each_value
@utils.filter_values
def issued_with_entry(self, key, value):
    """Issued With Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {"#": "Issued with", "8": "No display constant generated"}
    return {
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'record_control_number': value.get('w'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title': utils.force_list(
            value.get('t')
        ),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('preceding_entry', '^780[10_][_10325476]')
@utils.for_each_value
@utils.filter_values
def preceding_entry(self, key, value):
    """Preceding Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "0": "Continues",
        "1": "Continues in part",
        "2": "Supersedes",
        "3": "Supersedes in part",
        "4": "Formed by the union of ... and ...",
        "5": "Absorbed",
        "6": "Absorbed in part",
        "7": "Separated from"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'type_of_relationship': indicator_map2.get(key[4]),
    }


@inspiremarc.over('succeeding_entry', '^785[10_][_103254768]')
@utils.for_each_value
@utils.filter_values
def succeeding_entry(self, key, value):
    """Succeeding Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "0": "Continued by",
        "1": "Continued in part by",
        "2": "Superseded by",
        "3": "Superseded in part by",
        "4": "Absorbed by",
        "5": "Absorbed in part by",
        "6": "Split into ... and ...",
        "7": "Merged with ... to form ...",
        "8": "Changed back to"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'type_of_relationship': indicator_map2.get(key[4]),
    }


@inspiremarc.over('data_source_entry', '^786[10_][8_]')
@utils.for_each_value
@utils.filter_values
def data_source_entry(self, key, value):
    """Data Source Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {"#": "Data source", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'period_of_content': utils.force_list(
            value.get('j')
        ),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'abbreviated_title': utils.force_list(
            value.get('p')
        ),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'source_contribution': utils.force_list(
            value.get('v')
        ),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('other_relationship_entry', '^787[10_][8_]')
@utils.for_each_value
@utils.filter_values
def other_relationship_entry(self, key, value):
    """Other Relationship Entry."""
    indicator_map1 = {"0": "Display note", "1": "Do not display note"}
    indicator_map2 = {
        "#": "Related item", "8": "No display constant generated"}
    return {
        'relationship_code': value.get('4'),
        'control_subfield': utils.force_list(
            value.get('7')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'main_entry_heading': utils.force_list(
            value.get('a')
        ),
        'qualifying_information': utils.force_list(
            value.get('c')
        ),
        'edition': utils.force_list(
            value.get('b')
        ),
        'place_publisher_and_date_of_publication': utils.force_list(
            value.get('d')
        ),
        'related_parts': value.get('g'),
        'relationship_information': value.get('i'),
        'physical_description': utils.force_list(
            value.get('h')
        ),
        'series_data_for_related_item': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'other_item_identifier': value.get('o'),
        'note': value.get('n'),
        'uniform_title': utils.force_list(
            value.get('s')
        ),
        'report_number': value.get('r'),
        'standard_technical_report_number': utils.force_list(
            value.get('u')
        ),
        'title': utils.force_list(
            value.get('t')
        ),
        'record_control_number': value.get('w'),
        'coden_designation': utils.force_list(
            value.get('y')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'international_standard_book_number': value.get('z'),
        'note_controller': indicator_map1.get(key[3]),
        'display_constant_controller': indicator_map2.get(key[4]),
    }
