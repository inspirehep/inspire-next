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


@inspiremarc.over('abbreviated_title', '^210[10_][0_]')
@utils.for_each_value
@utils.filter_values
def abbreviated_title(self, key, value):
    """Abbreviated Title."""
    indicator_map1 = {"0": "No added entry", "1": "Added entry"}
    indicator_map2 = {
        "#": "Abbreviated key title", "0": "Other abbreviated title"}
    return {
        'abbreviated_title': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source': value.get('2'),
        'qualifying_information': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'title_added_entry': indicator_map1.get(key[3]),
        'type': indicator_map2.get(key[4]),
    }


@inspiremarc.over('key_title', '^222.[0_]')
@utils.for_each_value
@utils.filter_values
def key_title(self, key, value):
    """Key Title."""
    indicator_map2 = {"0": "No nonfiling characters"}
    return {
        'key_title': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'qualifying_information': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'nonfiling_characters': indicator_map2.get(key[4]),
    }


@inspiremarc.over('uniform_title', '^240[10_].')
@utils.filter_values
def uniform_title(self, key, value):
    """Uniform Title."""
    indicator_map1 = {
        "0": "Not printed or displayed", "1": "Printed or displayed"}
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
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_title_printed_or_displayed': indicator_map1.get(key[3]),
    }


@inspiremarc.over('translation_of_title_by_cataloging_agency', '^242[10_][0_]')
@utils.for_each_value
@utils.filter_values
def translation_of_title_by_cataloging_agency(self, key, value):
    """Translation of Title by Cataloging Agency."""
    indicator_map1 = {"0": "No added entry", "1": "Added entry"}
    indicator_map2 = {"0": "No nonfiling characters"}
    return {
        'title': utils.force_list(
            value.get('a')
        ),
        'statement_of_responsibility': utils.force_list(
            value.get('c')
        ),
        'remainder_of_title': utils.force_list(
            value.get('b')
        ),
        'medium': utils.force_list(
            value.get('h')
        ),
        'number_of_part_section_of_a_work': value.get('n'),
        'name_of_part_section_of_a_work': value.get('p'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'language_code_of_translated_title': utils.force_list(
            value.get('y')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title_added_entry': indicator_map1.get(key[3]),
        'nonfiling_characters': indicator_map2.get(key[4]),
    }


@inspiremarc.over('collective_uniform_title', '^243[10_].')
@utils.filter_values
def collective_uniform_title(self, key, value):
    """Collective Uniform Title."""
    indicator_map1 = {
        "0": "Not printed or displayed", "1": "Printed or displayed"}
    return {
        'uniform_title': utils.force_list(
            value.get('a')
        ),
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
        'name_of_part_section_of_a_work': value.get('p'),
        'version': utils.force_list(
            value.get('s')
        ),
        'key_for_music': utils.force_list(
            value.get('r')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_title_printed_or_displayed': indicator_map1.get(key[3]),
    }


@inspiremarc.over('title_statement', '^245[10_][0_]')
@utils.filter_values
def title_statement(self, key, value):
    """Title Statement."""
    indicator_map1 = {"0": "No added entry", "1": "Added entry"}
    indicator_map2 = {"0": "No nonfiling characters"}
    return {
        'title': utils.force_list(
            value.get('a')
        ),
        'statement_of_responsibility': utils.force_list(
            value.get('c')
        ),
        'remainder_of_title': utils.force_list(
            value.get('b')
        ),
        'bulk_dates': utils.force_list(
            value.get('g')
        ),
        'inclusive_dates': utils.force_list(
            value.get('f')
        ),
        'medium': utils.force_list(
            value.get('h')
        ),
        'form': value.get('k'),
        'number_of_part_section_of_a_work': value.get('n'),
        'name_of_part_section_of_a_work': value.get('p'),
        'version': utils.force_list(
            value.get('s')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title_added_entry': indicator_map1.get(key[3]),
        'nonfiling_characters': indicator_map2.get(key[4]),
    }


@inspiremarc.over('varying_form_of_title', '^246[1032_][_103254768]')
@utils.for_each_value
@utils.filter_values
def varying_form_of_title(self, key, value):
    """Varying Form of Title."""
    indicator_map1 = {
        "0": "Note, no added entry",
        "1": "Note, added entry",
        "2": "No note, no added entry",
        "3": "No note, added entry"}
    indicator_map2 = {
        "#": "No type specified",
        "0": "Portion of title",
        "1": "Parallel title",
        "2": "Distinctive title",
        "3": "Other title",
        "4": "Cover title",
        "5": "Added title page title",
        "6": "Caption title",
        "7": "Running title",
        "8": "Spine title"}
    return {
        'title_proper_short_title': utils.force_list(
            value.get('a')
        ),
        'remainder_of_title': utils.force_list(
            value.get('b')
        ),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_or_sequential_designation': utils.force_list(
            value.get('f')
        ),
        'display_text': utils.force_list(
            value.get('i')
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
        'note_added_entry_controller': indicator_map1.get(key[3]),
        'type_of_title': indicator_map2.get(key[4]),
    }


@inspiremarc.over('former_title', '^247[10_][10_]')
@utils.for_each_value
@utils.filter_values
def former_title(self, key, value):
    """Former Title."""
    indicator_map1 = {"0": "No added entry", "1": "Added entry"}
    indicator_map2 = {"0": "Display note", "1": "Do not display note"}
    return {
        'title': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'remainder_of_title': utils.force_list(
            value.get('b')
        ),
        'miscellaneous_information': utils.force_list(
            value.get('g')
        ),
        'date_or_sequential_designation': utils.force_list(
            value.get('f')
        ),
        'medium': utils.force_list(
            value.get('h')
        ),
        'number_of_part_section_of_a_work': value.get('n'),
        'name_of_part_section_of_a_work': value.get('p'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'title_added_entry': indicator_map1.get(key[3]),
        'note_controller': indicator_map2.get(key[4]),
    }
