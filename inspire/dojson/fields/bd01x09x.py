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


@inspiremarc.over('collections', '^980..')
@utils.for_each_value
@utils.filter_values
def collections(record, key, value):
    return {
        'primary': value.get('a'),
        'secondary': value.get('b'),
        'deleted': value.get('c'),
    }


@inspiremarc.over('library_of_congress_control_number', '^010..')
@utils.filter_values
def library_of_congress_control_number(self, key, value):
    """Library of Congress Control Number."""
    return {
        'lc_control_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'nucmc_control_number': value.get('b'),
        'canceled_invalid_lc_control_number': value.get('z'),
    }


@inspiremarc.over('patent_control_information', '^013..')
@utils.for_each_value
@utils.filter_values
def patent_control_information(self, key, value):
    """Patent Control Information."""
    return {
        'number': utils.force_list(
            value.get('a')
        ),
        'type_of_number': utils.force_list(
            value.get('c')
        ),
        'country': utils.force_list(
            value.get('b')
        ),
        'status': value.get('e'),
        'date': value.get('d'),
        'party_to_document': value.get('f'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('national_bibliography_number', '^015..')
@utils.for_each_value
@utils.filter_values
def national_bibliography_number(self, key, value):
    """National Bibliography Number."""
    return {
        'national_bibliography_number': value.get('a'),
        'qualifying_information': value.get('q'),
        'source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_national_bibliography_number': value.get('z'),
    }


@inspiremarc.over('national_bibliographic_agency_control_number', '^016[_7].')
@utils.for_each_value
@utils.filter_values
def national_bibliographic_agency_control_number(self, key, value):
    """National Bibliographic Agency Control Number."""
    indicator_map1 = {"#": "Library and Archives Canada",
                      "7": "Source specified in subfield $2"}
    return {
        'record_control_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source': utils.force_list(
            value.get('2')
        ),
        'canceled_invalid_control_number': value.get('z'),
        'national_bibliographic_agency': indicator_map1.get(key[3]),
    }


@inspiremarc.over('copyright_or_legal_deposit_number', '^017.[8_]')
@utils.for_each_value
@utils.filter_values
def copyright_or_legal_deposit_number(self, key, value):
    """Copyright or Legal Deposit Number."""
    indicator_map2 = {
        "#": "Copyright or legal deposit number",
        "8": "No display constant generated"}
    return {
        'copyright_or_legal_deposit_number': value.get('a'),
        'assigning_agency': utils.force_list(
            value.get('b')
        ),
        'date': utils.force_list(
            value.get('d')
        ),
        'display_text': utils.force_list(
            value.get('i')
        ),
        'source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_copyright_or_legal_deposit_number': value.get('z'),
        'display_constant_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('copyright_article_fee_code', '^018..')
@utils.filter_values
def copyright_article_fee_code(self, key, value):
    """Copyright Article-Fee Code."""
    return {
        'copyright_article_fee_code_nr': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('international_standard_book_number', '^020..')
@utils.for_each_value
@utils.filter_values
def international_standard_book_number(self, key, value):
    """International Standard Book Number."""
    return {
        'international_standard_book_number': utils.force_list(
            value.get('a')
        ),
        'terms_of_availability': utils.force_list(
            value.get('c')
        ),
        'qualifying_information': value.get('q'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_isbn': value.get('z'),
    }


@inspiremarc.over('international_standard_serial_number', '^022[10_].')
@utils.for_each_value
@utils.filter_values
def international_standard_serial_number(self, key, value):
    """International Standard Serial Number."""
    indicator_map1 = {
        "#": "No level specified",
        "0": "Continuing resource of international interest",
        "1": "Continuing resource not of international interest"}
    return {
        'international_standard_serial_number': utils.force_list(
            value.get('a')
        ),
        'canceled_issn_l': value.get('m'),
        'issn_l': utils.force_list(
            value.get('l')
        ),
        'source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'incorrect_issn': value.get('y'),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_issn': value.get('z'),
        'level_of_international_interest': indicator_map1.get(key[3]),
    }


@inspiremarc.over('other_standard_identifier', '^024[1032478_][10_]')
@utils.for_each_value
@utils.filter_values
def other_standard_identifier(self, key, value):
    """Other Standard Identifier."""
    indicator_map1 = {
        "0": "International Standard Recording Code",
        "1": "Universal Product Code",
        "2": "International Standard Music Number",
        "3": "International Article Number",
        "4": "Serial Item and Contribution Identifier",
        "7": "Source specified in subfield $2",
        "8": "Unspecified type of standard number or code"}
    indicator_map2 = {
        "#": "No information provided",
        "0": "No difference",
        "1": "Difference"}
    return {
        'standard_number_or_code': utils.force_list(
            value.get('a')),
        'terms_of_availability': utils.force_list(
            value.get('c')),
        'additional_codes_following_the_standard_number_or_code': utils.force_list(
            value.get('d')),
        'qualifying_information': value.get('q'),
        'source_of_number_or_code': utils.force_list(
            value.get('2')),
        'linkage': utils.force_list(
            value.get('6')),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_standard_number_or_code': value.get('z'),
        'type_of_standard_number_or_code': indicator_map1.get(
            key[3]),
        'difference_indicator': indicator_map2.get(
            key[4]),
    }


@inspiremarc.over('overseas_acquisition_number', '^025..')
@utils.for_each_value
@utils.filter_values
def overseas_acquisition_number(self, key, value):
    """Overseas Acquisition Number."""
    return {
        'overseas_acquisition_number': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('fingerprint_identifier', '^026..')
@utils.for_each_value
@utils.filter_values
def fingerprint_identifier(self, key, value):
    """Fingerprint Identifier."""
    return {
        'first_and_second_groups_of_characters': utils.force_list(
            value.get('a')
        ),
        'date': utils.force_list(
            value.get('c')
        ),
        'third_and_fourth_groups_of_characters': utils.force_list(
            value.get('b')
        ),
        'unparsed_fingerprint': utils.force_list(
            value.get('e')
        ),
        'number_of_volume_or_part': value.get('d'),
        'source': utils.force_list(
            value.get('2')
        ),
        'institution_to_which_field_applies': value.get('5'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('standard_technical_report_number', '^027..')
@utils.for_each_value
@utils.filter_values
def standard_technical_report_number(self, key, value):
    """Standard Technical Report Number."""
    return {
        'standard_technical_report_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_number': value.get('z'),
        'qualifying_information': value.get('q'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('publisher_number', '^028[103254_][1032_]')
@utils.for_each_value
@utils.filter_values
def publisher_number(self, key, value):
    """Publisher Number."""
    indicator_map1 = {
        "0": "Issue number",
        "1": "Matrix number",
        "2": "Plate number",
        "3": "Other music number",
        "4": "Videorecording number",
        "5": "Other publisher number"}
    indicator_map2 = {"0": "No note, no added entry", "1": "Note, added entry",
                      "2": "Note, no added entry", "3": "No note, added entry"}
    return {
        'publisher_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source': utils.force_list(
            value.get('b')
        ),
        'qualifying_information': value.get('q'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'type_of_publisher_number': indicator_map1.get(key[3]),
        'note_added_entry_controller': indicator_map2.get(key[4]),
    }


@inspiremarc.over('coden_designation', '^030..')
@utils.for_each_value
@utils.filter_values
def coden_designation(self, key, value):
    """CODEN Designation."""
    return {
        'coden': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_coden': value.get('z'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('musical_incipits_information', '^031..')
@utils.for_each_value
@utils.filter_values
def musical_incipits_information(self, key, value):
    """Musical Incipits Information."""
    return {
        'number_of_work': utils.force_list(
            value.get('a')
        ),
        'number_of_excerpt': utils.force_list(
            value.get('c')
        ),
        'number_of_movement': utils.force_list(
            value.get('b')
        ),
        'role': utils.force_list(
            value.get('e')
        ),
        'caption_or_heading': value.get('d'),
        'clef': utils.force_list(
            value.get('g')
        ),
        'public_note': value.get('z'),
        'voice_instrument': utils.force_list(
            value.get('m')
        ),
        'time_signature': utils.force_list(
            value.get('o')
        ),
        'key_signature': utils.force_list(
            value.get('n')
        ),
        'general_note': value.get('q'),
        'musical_notation': utils.force_list(
            value.get('p')
        ),
        'coded_validity_note': value.get('s'),
        'system_code': utils.force_list(
            value.get('2')
        ),
        'uniform_resource_identifier': value.get('u'),
        'text_incipit': value.get('t'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'link_text': value.get('y'),
        'field_link_and_sequence_number': value.get('8'),
        'key_or_mode': utils.force_list(
            value.get('r')
        ),
    }


@inspiremarc.over('postal_registration_number', '^032..')
@utils.for_each_value
@utils.filter_values
def postal_registration_number(self, key, value):
    """Postal Registration Number."""
    return {
        'postal_registration_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source_agency_assigning_number': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('date_time_and_place_of_an_event', '^033[10_2][10_2]')
@utils.for_each_value
@utils.filter_values
def date_time_and_place_of_an_event(self, key, value):
    """Date/Time and Place of an Event."""
    indicator_map1 = {"#": "No date information ", "0": "Single date ",
                      "1": "Multiple single dates ", "2": "Range of dates "}
    indicator_map2 = {"#": "No information provided ",
                      "0": "Capture ", "1": "Broadcast ", "2": "Finding "}
    return {
        'formatted_date_time': value.get('a'),
        'geographic_classification_subarea_code': value.get('c'),
        'geographic_classification_area_code': value.get('b'),
        'place_of_event': value.get('p'),
        'authority_record_control_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_term': value.get('2'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'type_of_date_in_subfield_a': indicator_map1.get(key[3]),
        'type_of_event': indicator_map2.get(key[4]),
    }


@inspiremarc.over('coded_cartographic_mathematical_data', '^034[103_][10_]')
@utils.for_each_value
@utils.filter_values
def coded_cartographic_mathematical_data(self, key, value):
    """Coded Cartographic Mathematical Data."""
    indicator_map1 = {"0": "Scale indeterminable/No scale recorded",
                      "1": "Single scale", "3": "Range of scales"}
    indicator_map2 = {
        "#": "Not applicable", "0": "Outer ring", "1": "Exclusion ring"}
    return {
        'authority_record_control_number_or_standard_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'category_of_scale': utils.force_list(
            value.get('a')
        ),
        'constant_ratio_linear_vertical_scale': value.get('c'),
        'constant_ratio_linear_horizontal_scale': value.get('b'),
        'coordinates_easternmost_longitude': utils.force_list(
            value.get('e')
        ),
        'coordinates_westernmost_longitude': utils.force_list(
            value.get('d')
        ),
        'coordinates_southernmost_latitude': utils.force_list(
            value.get('g')
        ),
        'coordinates_northernmost_latitude': utils.force_list(
            value.get('f')
        ),
        'angular_scale': value.get('h'),
        'declination_southern_limit': utils.force_list(
            value.get('k')
        ),
        'declination_northern_limit': utils.force_list(
            value.get('j')
        ),
        'right_ascension_eastern_limit': utils.force_list(
            value.get('m')
        ),
        'right_ascension_western_limit': utils.force_list(
            value.get('n')
        ),
        'equinox': utils.force_list(
            value.get('p')
        ),
        'g_ring_latitude': value.get('s'),
        'distance_from_earth': utils.force_list(
            value.get('r')
        ),
        'g_ring_longitude': value.get('t'),
        'ending_date': utils.force_list(
            value.get('y')
        ),
        'beginning_date': utils.force_list(
            value.get('x')
        ),
        'name_of_extraterrestrial_body': utils.force_list(
            value.get('z')
        ),
        'type_of_scale': indicator_map1.get(key[3]),
        'type_of_ring': indicator_map2.get(key[4]),
    }


@inspiremarc.over('system_control_number', '^035..')
@utils.for_each_value
@utils.filter_values
def system_control_number(self, key, value):
    """System Control Number."""
    return {
        'system_control_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_control_number': value.get('z'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('original_study_number_for_computer_data_files', '^036..')
@utils.filter_values
def original_study_number_for_computer_data_files(self, key, value):
    """Original Study Number for Computer Data Files."""
    return {
        'original_study_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source_agency_assigning_number': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('source_of_acquisition', '^037..')
@utils.for_each_value
@utils.filter_values
def source_of_acquisition(self, key, value):
    """Source of Acquisition."""
    return {
        'stock_number': utils.force_list(
            value.get('a')
        ),
        'terms_of_availability': value.get('c'),
        'source_of_stock_number_acquisition': utils.force_list(
            value.get('b')
        ),
        'additional_format_characteristics': value.get('g'),
        'form_of_issue': value.get('f'),
        'note': value.get('n'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('record_content_licensor', '^038..')
@utils.filter_values
def record_content_licensor(self, key, value):
    """Record Content Licensor."""
    return {
        'record_content_licensor': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('cataloging_source', '^040..')
@utils.filter_values
def cataloging_source(self, key, value):
    """Cataloging Source."""
    return {
        'original_cataloging_agency': utils.force_list(
            value.get('a')
        ),
        'transcribing_agency': utils.force_list(
            value.get('c')
        ),
        'language_of_cataloging': utils.force_list(
            value.get('b')
        ),
        'description_conventions': value.get('e'),
        'modifying_agency': value.get('d'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('language_code', '^041[10_].')
@utils.for_each_value
@utils.filter_values
def language_code(self, key, value):
    """Language Code."""
    indicator_map1 = {
        "#": "No information provided",
        "0": "Item not a translation/does not include a translation",
        "1": "Item is or includes a translation"}
    return {
        'language_code_of_text_sound_track_or_separate_title': value.get('a'),
        'language_code_of_summary_or_abstract': value.get('b'),
        'language_code_of_librettos': value.get('e'),
        'language_code_of_sung_or_spoken_text': value.get('d'),
        'language_code_of_accompanying_material_other_than_librettos': value.get('g'),
        'language_code_of_table_of_contents': value.get('f'),
        'language_code_of_original': value.get('h'),
        'language_code_of_intermediate_translations': value.get('k'),
        'language_code_of_subtitles_or_captions': value.get('j'),
        'language_code_of_original_accompanying_materials_other_than_librettos': value.get('m'),
        'language_code_of_original_libretto': value.get('n'),
        'source_of_code': utils.force_list(
            value.get('2')),
        'linkage': utils.force_list(
            value.get('6')),
        'field_link_and_sequence_number': value.get('8'),
        'translation_indication': indicator_map1.get(
            key[3]),
    }


@inspiremarc.over('authentication_code', '^042..')
@utils.filter_values
def authentication_code(self, key, value):
    """Authentication Code."""
    return {
        'authentication_code': value.get('a'),
    }


@inspiremarc.over('geographic_area_code', '^043..')
@utils.filter_values
def geographic_area_code(self, key, value):
    """Geographic Area Code."""
    return {
        'geographic_area_code': value.get('a'),
        'iso_code': value.get('c'),
        'local_gac_code': value.get('b'),
        'authority_record_control_number_or_standard_number': value.get('0'),
        'source_of_local_code': value.get('2'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('country_of_publishing_producing_entity_code', '^044..')
@utils.filter_values
def country_of_publishing_producing_entity_code(self, key, value):
    """Country of Publishing/Producing Entity Code."""
    return {
        'marc_country_code': value.get('a'),
        'iso_country_code': value.get('c'),
        'local_subentity_code': value.get('b'),
        'source_of_local_subentity_code': value.get('2'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('time_period_of_content', '^045[10_2].')
@utils.filter_values
def time_period_of_content(self, key, value):
    """Time Period of Content."""
    indicator_map1 = {
        "#": "Subfield $b or $c not present",
        "0": "Single date/time",
        "1": "Multiple single dates/times",
        "2": "Range of dates/times"}
    return {
        'time_period_code': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'formatted_pre_9999_bc_time_period': value.get('c'),
        'formatted_9999_bc_through_ce_time_period': value.get('b'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'type_of_time_period_in_subfield_b_or_c': indicator_map1.get(key[3]),
    }


@inspiremarc.over('special_coded_dates', '^046..')
@utils.for_each_value
@utils.filter_values
def special_coded_dates(self, key, value):
    """Special Coded Dates."""
    return {
        'type_of_date_code': utils.force_list(
            value.get('a')
        ),
        'date_1_ce_date': utils.force_list(
            value.get('c')
        ),
        'date_1_bc_date': utils.force_list(
            value.get('b')
        ),
        'date_2_ce_date': utils.force_list(
            value.get('e')
        ),
        'date_2_bc_date': utils.force_list(
            value.get('d')
        ),
        'beginning_or_single_date_created': utils.force_list(
            value.get('k')
        ),
        'date_resource_modified': utils.force_list(
            value.get('j')
        ),
        'beginning_of_date_valid': utils.force_list(
            value.get('m')
        ),
        'ending_date_created': utils.force_list(
            value.get('l')
        ),
        'single_or_starting_date_for_aggregated_content': utils.force_list(
            value.get('o')
        ),
        'end_of_date_valid': utils.force_list(
            value.get('n')
        ),
        'ending_date_for_aggregated_content': utils.force_list(
            value.get('p')
        ),
        'source_of_date': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('form_of_musical_composition_code', '^047..')
@utils.for_each_value
@utils.filter_values
def form_of_musical_composition_code(self, key, value):
    """Form of Musical Composition Code."""
    return {
        'form_of_musical_composition_code': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'source_of_code': utils.force_list(
            value.get('2')
        ),
    }


@inspiremarc.over('number_of_musical_instruments_or_voices_code', '^048..')
@utils.for_each_value
@utils.filter_values
def number_of_musical_instruments_or_voices_code(self, key, value):
    """Number of Musical Instruments or Voices Code."""
    return {
        'performer_or_ensemble': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'source_of_code': utils.force_list(
            value.get('2')
        ),
        'soloist': value.get('b'),
    }


@inspiremarc.over('library_of_congress_call_number', '^050[10_][0_4]')
@utils.for_each_value
@utils.filter_values
def library_of_congress_call_number(self, key, value):
    """Library of Congress Call Number."""
    indicator_map1 = {"#": "No information provided",
                      "0": "Item is in LC", "1": "Item is not in LC"}
    indicator_map2 = {
        "0": "Assigned by LC", "4": "Assigned by agency other than LC"}
    return {
        'classification_number': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'item_number': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'existence_in_lc_collection': indicator_map1.get(key[3]),
        'source_of_call_number': indicator_map2.get(key[4]),
    }


@inspiremarc.over('library_of_congress_copy_issue_offprint_statement', '^051..')
@utils.for_each_value
@utils.filter_values
def library_of_congress_copy_issue_offprint_statement(self, key, value):
    """Library of Congress Copy, Issue, Offprint Statement."""
    return {
        'classification_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'copy_information': utils.force_list(
            value.get('c')
        ),
        'item_number': utils.force_list(
            value.get('b')
        ),
    }


@inspiremarc.over('geographic_classification', '^052..')
@utils.for_each_value
@utils.filter_values
def geographic_classification(self, key, value):
    """Geographic Classification."""
    return {
        'geographic_classification_area_code': utils.force_list(
            value.get('a')
        ),
        'geographic_classification_subarea_code': value.get('b'),
        'populated_place_name': value.get('d'),
        'code_source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over(
    'classification_numbers_assigned_in_canada', '^055[10_][_1032547698]')
@utils.for_each_value
@utils.filter_values
def classification_numbers_assigned_in_canada(self, key, value):
    """Classification Numbers Assigned in Canada."""
    indicator_map1 = {"#": "Information not provided",
                      "0": "Work held by LAC", "1": "Work not held by LAC"}
    indicator_map2 = {
        "0": "LC-based call number assigned by LAC",
        "1": "Complete LC class number assigned by LAC",
        "2": "Incomplete LC class number assigned by LAC",
        "3": "LC-based call number assigned by the contributing library",
        "4": "Complete LC class number assigned by the contributing library",
        "5": "Incomplete LC class number assigned by the contributing library",
        "6": "Other call number assigned by LAC",
        "7": "Other class number assigned by LAC",
        "8": "Other call number assigned by the contributing library",
        "9": "Other class number assigned by the contributing library"}
    return {
        'classification_number': utils.force_list(
            value.get('a')),
        'field_link_and_sequence_number': value.get('8'),
        'source_of_call_class_number': utils.force_list(
            value.get('2')),
        'item_number': utils.force_list(
            value.get('b')),
        'linkage': utils.force_list(
            value.get('6')),
        'existence_in_lac_collection': indicator_map1.get(
            key[3]),
        'type_completeness_source_of_class_call_number': indicator_map2.get(
            key[4]),
    }


@inspiremarc.over('national_library_of_medicine_call_number', '^060[10_][0_4]')
@utils.for_each_value
@utils.filter_values
def national_library_of_medicine_call_number(self, key, value):
    """National Library of Medicine Call Number."""
    indicator_map1 = {"#": "No information provided",
                      "0": "Item is in NLM", "1": "Item is not in NLM"}
    indicator_map2 = {
        "0": "Assigned by NLM", "4": "Assigned by agency other than NLM"}
    return {
        'classification_number_r': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'item_number': utils.force_list(
            value.get('b')
        ),
        'existence_in_nlm_collection': indicator_map1.get(key[3]),
        'source_of_call_number': indicator_map2.get(key[4]),
    }


@inspiremarc.over('national_library_of_medicine_copy_statement', '^061..')
@utils.for_each_value
@utils.filter_values
def national_library_of_medicine_copy_statement(self, key, value):
    """National Library of Medicine Copy Statement."""
    return {
        'classification_number': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'copy_information': utils.force_list(
            value.get('c')
        ),
        'item_number': utils.force_list(
            value.get('b')
        ),
    }


@inspiremarc.over('character_sets_present', '^066..')
@utils.filter_values
def character_sets_present(self, key, value):
    """Character Sets Present."""
    return {
        'primary_g0_character_set': utils.force_list(
            value.get('a')
        ),
        'alternate_g0_or_g1_character_set': value.get('c'),
        'primary_g1_character_set': utils.force_list(
            value.get('b')
        ),
    }


@inspiremarc.over('national_agricultural_library_call_number', '^070[10_].')
@utils.for_each_value
@utils.filter_values
def national_agricultural_library_call_number(self, key, value):
    """National Agricultural Library Call Number."""
    indicator_map1 = {"0": "Item is in NAL", "1": "Item is not in NAL"}
    return {
        'classification_number': value.get('a'),
        'field_link_and_sequence_number_r': value.get('8'),
        'item_number': utils.force_list(
            value.get('b')
        ),
        'existence_in_nal_collection': indicator_map1.get(key[3]),
    }


@inspiremarc.over('national_agricultural_library_copy_statement', '^071..')
@utils.for_each_value
@utils.filter_values
def national_agricultural_library_copy_statement(self, key, value):
    """National Agricultural Library Copy Statement."""
    return {
        'classification_number': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'copy_information': value.get('c'),
        'item_number': utils.force_list(
            value.get('b')
        ),
    }


@inspiremarc.over('subject_category_code', '^072..')
@utils.for_each_value
@utils.filter_values
def subject_category_code(self, key, value):
    """Subject Category Code."""
    return {
        'subject_category_code': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source': utils.force_list(
            value.get('2')
        ),
        'subject_category_code_subdivision': value.get('x'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('gpo_item_number', '^074..')
@utils.for_each_value
@utils.filter_values
def gpo_item_number(self, key, value):
    """GPO Item Number."""
    return {
        'gpo_item_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_gpo_item_number': value.get('z'),
    }


@inspiremarc.over('universal_decimal_classification_number', '^080[10_].')
@utils.for_each_value
@utils.filter_values
def universal_decimal_classification_number(self, key, value):
    """Universal Decimal Classification Number."""
    indicator_map1 = {
        "#": "No information provided", "0": "Full", "1": "Abridged"}
    return {
        'universal_decimal_classification_number': utils.force_list(
            value.get('a')
        ),
        'item_number': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'edition_identifier': utils.force_list(
            value.get('2')
        ),
        'common_auxiliary_subdivision': value.get('x'),
        'field_link_and_sequence_number': value.get('8'),
        'type_of_edition': indicator_map1.get(key[3]),
    }


@inspiremarc.over('dewey_decimal_classification_number', '^082[10_7][0_4]')
@utils.for_each_value
@utils.filter_values
def dewey_decimal_classification_number(self, key, value):
    """Dewey Decimal Classification Number."""
    indicator_map1 = {"0": "Full edition", "1": "Abridged edition",
                      "7": "Other edition specified in subfield $2"}
    indicator_map2 = {
        "#": "No information provided",
        "0": "Assigned by LC",
        "4": "Assigned by agency other than LC"}
    return {
        'classification_number': value.get('a'),
        'item_number': utils.force_list(
            value.get('b')
        ),
        'standard_or_optional_designation': utils.force_list(
            value.get('m')
        ),
        'assigning_agency': utils.force_list(
            value.get('q')
        ),
        'edition_number': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'type_of_edition': indicator_map1.get(key[3]),
        'source_of_classification_number': indicator_map2.get(key[4]),
    }


@inspiremarc.over('additional_dewey_decimal_classification_number', '^083[10_7].')
@utils.for_each_value
@utils.filter_values
def additional_dewey_decimal_classification_number(self, key, value):
    """Additional Dewey Decimal Classification Number."""
    indicator_map1 = {"0": "Full edition", "1": "Abridged edition",
                      "7": "Other edition specified in subfield $2"}
    return {
        'classification_number': value.get('a'),
        'classification_number_ending_number_of_span': value.get('c'),
        'standard_or_optional_designation': utils.force_list(
            value.get('m')),
        'assigning_agency': utils.force_list(
            value.get('q')),
        'edition_number': utils.force_list(
            value.get('2')),
        'linkage': utils.force_list(
            value.get('6')),
        'table_sequence_number_for_internal_subarrangement_or_add_table': value.get('y'),
        'field_link_and_sequence_number': value.get('8'),
        'table_identification': value.get('z'),
        'type_of_edition': indicator_map1.get(
            key[3]),
    }


@inspiremarc.over('other_classification_number', '^084..')
@utils.for_each_value
@utils.filter_values
def other_classification_number(self, key, value):
    """Other Classification Number."""
    return {
        'classification_number': value.get('a'),
        'item_number': utils.force_list(
            value.get('b')
        ),
        'assigning_agency': utils.force_list(
            value.get('q')
        ),
        'number_source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('synthesized_classification_number_components', '^085..')
@utils.for_each_value
@utils.filter_values
def synthesized_classification_number_components(self, key, value):
    """Synthesized Classification Number Components."""
    return {
        'number_where_instructions_are_found_single_number_or_beginning_number_of_span': value.get('a'),
        'classification_number_ending_number_of_span': value.get('c'),
        'base_number': value.get('b'),
        'facet_designator': value.get('f'),
        'number_in_internal_subarrangement_or_add_table_where_instructions_are_found': value.get('v'),
        'digits_added_from_classification_number_in_schedule_or_external_table': value.get('s'),
        'root_number': value.get('r'),
        'number_being_analyzed': value.get('u'),
        'digits_added_from_internal_subarrangement_or_add_table': value.get('t'),
        'table_identification_internal_subarrangement_or_add_table': value.get('w'),
        'linkage': utils.force_list(
            value.get('6')),
        'table_sequence_number_for_internal_subarrangement_or_add_table': value.get('y'),
        'field_link_and_sequence_number': value.get('8'),
        'table_identification': value.get('z'),
    }


@inspiremarc.over('government_document_classification_number', '^086..')
@utils.for_each_value
@utils.filter_values
def government_document_classification_number(self, key, value):
    """Government Document Classification Number."""
    return {
        'classification_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'number_source': utils.force_list(
            value.get('2')
        ),
        'canceled_invalid_classification_number': value.get('z'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('report_number', '^088..')
@utils.for_each_value
@utils.filter_values
def report_number(self, key, value):
    """Report Number."""
    return {
        'report_number': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'canceled_invalid_report_number': value.get('z'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }
