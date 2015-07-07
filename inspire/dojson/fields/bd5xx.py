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


@inspiremarc.over('general_note', '^500..')
@utils.for_each_value
@utils.filter_values
def general_note(self, key, value):
    """General Note."""
    return {
        'general_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('with_note', '^501..')
@utils.for_each_value
@utils.filter_values
def with_note(self, key, value):
    """With Note."""
    return {
        'with_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('dissertation_note', '^502..')
@utils.for_each_value
@utils.filter_values
def dissertation_note(self, key, value):
    """Dissertation Note."""
    return {
        'dissertation_note': utils.force_list(
            value.get('a')
        ),
        'name_of_granting_institution': utils.force_list(
            value.get('c')
        ),
        'degree_type': utils.force_list(
            value.get('b')
        ),
        'year_degree_granted': utils.force_list(
            value.get('d')
        ),
        'miscellaneous_information': value.get('g'),
        'dissertation_identifier': value.get('o'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('bibliography_note', '^504..')
@utils.for_each_value
@utils.filter_values
def bibliography_note(self, key, value):
    """Bibliography, Etc. Note."""
    return {
        'bibliography_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'number_of_references': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('formatted_contents_note', '^505[10_28][0_]')
@utils.for_each_value
@utils.filter_values
def formatted_contents_note(self, key, value):
    """Formatted Contents Note."""
    indicator_map1 = {
        "0": "Contents",
        "1": "Incomplete contents",
        "2": "Partial contents",
        "8": "No display constant generated"}
    indicator_map2 = {"#": "Basic", "0": "Enhanced"}
    return {
        'formatted_contents_note': utils.force_list(
            value.get('a')
        ),
        'miscellaneous_information': value.get('g'),
        'statement_of_responsibility': value.get('r'),
        'uniform_resource_identifier': value.get('u'),
        'title': value.get('t'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_constant_controller': indicator_map1.get(key[3]),
        'level_of_content_designation': indicator_map2.get(key[4]),
    }


@inspiremarc.over('restrictions_on_access_note', '^506[10_].')
@utils.for_each_value
@utils.filter_values
def restrictions_on_access_note(self, key, value):
    """Restrictions on Access Note."""
    indicator_map1 = {"#": "No information provided",
                      "0": "No restrictions", "1": "Restrictions apply"}
    return {
        'terms_governing_access': utils.force_list(
            value.get('a')
        ),
        'physical_access_provisions': value.get('c'),
        'jurisdiction': value.get('b'),
        'authorization': value.get('e'),
        'authorized_users': value.get('d'),
        'standardized_terminology_for_access_restriction': value.get('f'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_term': utils.force_list(
            value.get('2')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_resource_identifier': value.get('u'),
        'restriction': indicator_map1.get(key[3]),
    }


@inspiremarc.over('scale_note_for_graphic_material', '^507..')
@utils.filter_values
def scale_note_for_graphic_material(self, key, value):
    """Scale Note for Graphic Material."""
    return {
        'representative_fraction_of_scale_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'remainder_of_scale_note': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('creation_production_credits_note', '^508..')
@utils.for_each_value
@utils.filter_values
def creation_production_credits_note(self, key, value):
    """Creation/Production Credits Note."""
    return {
        'creation_production_credits_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('citation_references_note', '^510[10324_].')
@utils.for_each_value
@utils.filter_values
def citation_references_note(self, key, value):
    """Citation/References Note."""
    indicator_map1 = {
        "0": "Coverage unknown",
        "1": "Coverage complete",
        "2": "Coverage is selective",
        "3": "Location in source not given",
        "4": "Location in source given"}
    return {
        'name_of_source': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': utils.force_list(
            value.get('x')
        ),
        'location_within_source': utils.force_list(
            value.get('c')
        ),
        'coverage_of_source': utils.force_list(
            value.get('b')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'coverage_location_in_source': indicator_map1.get(key[3]),
    }


@inspiremarc.over('participant_or_performer_note', '^511[10_].')
@utils.for_each_value
@utils.filter_values
def participant_or_performer_note(self, key, value):
    """Participant or Performer Note."""
    indicator_map1 = {"0": "No display constant generated", "1": "Cast"}
    return {
        'participant_or_performer_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('type_of_report_and_period_covered_note', '^513..')
@utils.for_each_value
@utils.filter_values
def type_of_report_and_period_covered_note(self, key, value):
    """Type of Report and Period Covered Note."""
    return {
        'type_of_report': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'period_covered': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('data_quality_note', '^514..')
@utils.filter_values
def data_quality_note(self, key, value):
    """Data Quality Note."""
    return {
        'attribute_accuracy_report': utils.force_list(
            value.get('a')
        ),
        'attribute_accuracy_explanation': value.get('c'),
        'attribute_accuracy_value': value.get('b'),
        'completeness_report': utils.force_list(
            value.get('e')
        ),
        'logical_consistency_report': utils.force_list(
            value.get('d')
        ),
        'horizontal_position_accuracy_value': value.get('g'),
        'horizontal_position_accuracy_report': utils.force_list(
            value.get('f')
        ),
        'vertical_positional_accuracy_report': utils.force_list(
            value.get('i')
        ),
        'horizontal_position_accuracy_explanation': value.get('h'),
        'vertical_positional_accuracy_explanation': value.get('k'),
        'vertical_positional_accuracy_value': value.get('j'),
        'cloud_cover': utils.force_list(
            value.get('m')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_note': value.get('z'),
    }


@inspiremarc.over('numbering_peculiarities_note', '^515..')
@utils.for_each_value
@utils.filter_values
def numbering_peculiarities_note(self, key, value):
    """Numbering Peculiarities Note."""
    return {
        'numbering_peculiarities_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('type_of_computer_file_or_data_note', '^516[8_].')
@utils.for_each_value
@utils.filter_values
def type_of_computer_file_or_data_note(self, key, value):
    """Type of Computer File or Data Note."""
    indicator_map1 = {
        "#": "Type of file", "8": "No display constant generated"}
    return {
        'type_of_computer_file_or_data_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('date_time_and_place_of_an_event_note', '^518..')
@utils.for_each_value
@utils.filter_values
def date_time_and_place_of_an_event_note(self, key, value):
    """Date/Time and Place of an Event Note."""
    return {
        'date_time_and_place_of_an_event_note': utils.force_list(
            value.get('a')
        ),
        'date_of_event': value.get('d'),
        'place_of_event': value.get('p'),
        'other_event_information': value.get('o'),
        'record_control_number': value.get('0'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_term': value.get('2'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('summary', '^520[10_2483].')
@utils.for_each_value
@utils.filter_values
def summary(self, key, value):
    """Summary, Etc.."""
    indicator_map1 = {
        "#": "Summary",
        "0": "Subject",
        "1": "Review",
        "2": "Scope and content",
        "3": "Abstract",
        "4": "Content advice",
        "8": "No display constant generated"}
    return {
        'summary': utils.force_list(
            value.get('a')
        ),
        'assigning_source': utils.force_list(
            value.get('c')
        ),
        'expansion_of_summary_note': utils.force_list(
            value.get('b')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source': utils.force_list(
            value.get('2')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('target_audience_note', '^521[10_2483].')
@utils.for_each_value
@utils.filter_values
def target_audience_note(self, key, value):
    """Target Audience Note."""
    indicator_map1 = {
        "#": "Audience",
        "0": "Reading grade level",
        "1": "Interest age level",
        "2": "Interest grade level",
        "3": "Special audience characteristics",
        "4": "Motivation/interest level",
        "8": "No display constant generated"}
    return {
        'target_audience_note': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('geographic_coverage_note', '^522[8_].')
@utils.for_each_value
@utils.filter_values
def geographic_coverage_note(self, key, value):
    """Geographic Coverage Note."""
    indicator_map1 = {
        "#": "Geographic coverage", "8": "No display constant generated"}
    return {
        'geographic_coverage_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('preferred_citation_of_described_materials_note', '^524[8_].')
@utils.for_each_value
@utils.filter_values
def preferred_citation_of_described_materials_note(self, key, value):
    """Preferred Citation of Described Materials Note."""
    indicator_map1 = {"#": "Cite as", "8": "No display constant generated"}
    return {
        'preferred_citation_of_described_materials_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_schema_used': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('supplement_note', '^525..')
@utils.for_each_value
@utils.filter_values
def supplement_note(self, key, value):
    """Supplement Note."""
    return {
        'supplement_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('study_program_information_note', '^526[0_8].')
@utils.for_each_value
@utils.filter_values
def study_program_information_note(self, key, value):
    """Study Program Information Note."""
    indicator_map1 = {
        "0": "Reading program", "8": "No display constant generated"}
    return {
        'program_name': utils.force_list(
            value.get('a')
        ),
        'nonpublic_note': value.get('x'),
        'reading_level': utils.force_list(
            value.get('c')
        ),
        'interest_level': utils.force_list(
            value.get('b')
        ),
        'title_point_value': utils.force_list(
            value.get('d')
        ),
        'display_text': utils.force_list(
            value.get('i')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'public_note': value.get('z'),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('additional_physical_form_available_note', '^530..')
@utils.for_each_value
@utils.filter_values
def additional_physical_form_available_note(self, key, value):
    """Additional Physical Form Available Note."""
    return {
        'additional_physical_form_available_note': utils.force_list(
            value.get('a')
        ),
        'availability_conditions': utils.force_list(
            value.get('c')
        ),
        'availability_source': utils.force_list(
            value.get('b')
        ),
        'order_number': utils.force_list(
            value.get('d')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('reproduction_note', '^533..')
@utils.for_each_value
@utils.filter_values
def reproduction_note(self, key, value):
    """Reproduction Note."""
    return {
        'type_of_reproduction': utils.force_list(
            value.get('a')),
        'agency_responsible_for_reproduction': value.get('c'),
        'place_of_reproduction': value.get('b'),
        'physical_description_of_reproduction': utils.force_list(
            value.get('e')),
        'date_of_reproduction': utils.force_list(
            value.get('d')),
        'series_statement_of_reproduction': value.get('f'),
        'dates_and_or_sequential_designation_of_issues_reproduced': value.get('m'),
        'note_about_reproduction': value.get('n'),
        'materials_specified': utils.force_list(
            value.get('3')),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')),
        'fixed_length_data_elements_of_reproduction': utils.force_list(
            value.get('7')),
        'linkage': utils.force_list(
            value.get('6')),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('original_version_note', '^534..')
@utils.for_each_value
@utils.filter_values
def original_version_note(self, key, value):
    """Original Version Note."""
    return {
        'main_entry_of_original': utils.force_list(
            value.get('a')
        ),
        'international_standard_serial_number': value.get('x'),
        'publication_distribution_of_original': utils.force_list(
            value.get('c')
        ),
        'edition_statement_of_original': utils.force_list(
            value.get('b')
        ),
        'physical_description_of_original': utils.force_list(
            value.get('e')
        ),
        'series_statement_of_original': value.get('f'),
        'key_title_of_original': value.get('k'),
        'material_specific_details': utils.force_list(
            value.get('m')
        ),
        'location_of_original': utils.force_list(
            value.get('l')
        ),
        'other_resource_identifier': value.get('o'),
        'note_about_original': value.get('n'),
        'introductory_phrase': utils.force_list(
            value.get('p')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'title_statement_of_original': utils.force_list(
            value.get('t')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'international_standard_book_number': value.get('z'),
    }


@inspiremarc.over('location_of_originals_duplicates_note', '^535[1_2].')
@utils.for_each_value
@utils.filter_values
def location_of_originals_duplicates_note(self, key, value):
    """Location of Originals/Duplicates Note."""
    indicator_map1 = {"1": "Holder of originals", "2": "Holder of duplicates"}
    return {
        'custodian': utils.force_list(
            value.get('a')
        ),
        'country': value.get('c'),
        'postal_address': value.get('b'),
        'telecommunications_address': value.get('d'),
        'repository_location_code': utils.force_list(
            value.get('g')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'custodial_role': indicator_map1.get(key[3]),
    }


@inspiremarc.over('funding_information_note', '^536..')
@utils.for_each_value
@utils.filter_values
def funding_information_note(self, key, value):
    """Funding Information Note."""
    return {
        'text_of_note': utils.force_list(
            value.get('a')
        ),
        'grant_number': value.get('c'),
        'contract_number': value.get('b'),
        'program_element_number': value.get('e'),
        'undifferentiated_number': value.get('d'),
        'task_number': value.get('g'),
        'project_number': value.get('f'),
        'work_unit_number': value.get('h'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('system_details_note', '^538..')
@utils.for_each_value
@utils.filter_values
def system_details_note(self, key, value):
    """System Details Note."""
    return {
        'system_details_note': utils.force_list(
            value.get('a')
        ),
        'display_text': utils.force_list(
            value.get('i')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': value.get('5'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_resource_identifier': value.get('u'),
    }


@inspiremarc.over('terms_governing_use_and_reproduction_note', '^540..')
@utils.for_each_value
@utils.filter_values
def terms_governing_use_and_reproduction_note(self, key, value):
    """Terms Governing Use and Reproduction Note."""
    return {
        'terms_governing_use_and_reproduction': utils.force_list(
            value.get('a')
        ),
        'authorization': utils.force_list(
            value.get('c')
        ),
        'jurisdiction': utils.force_list(
            value.get('b')
        ),
        'authorized_users': utils.force_list(
            value.get('d')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_resource_identifier': value.get('u'),
    }


@inspiremarc.over('immediate_source_of_acquisition_note', '^541[10_].')
@utils.for_each_value
@utils.filter_values
def immediate_source_of_acquisition_note(self, key, value):
    """Immediate Source of Acquisition Note."""
    indicator_map1 = {
        "#": "No information provided", "0": "Private", "1": "Not private"}
    return {
        'source_of_acquisition': utils.force_list(
            value.get('a')
        ),
        'method_of_acquisition': utils.force_list(
            value.get('c')
        ),
        'address': utils.force_list(
            value.get('b')
        ),
        'accession_number': utils.force_list(
            value.get('e')
        ),
        'date_of_acquisition': utils.force_list(
            value.get('d')
        ),
        'owner': utils.force_list(
            value.get('f')
        ),
        'purchase_price': utils.force_list(
            value.get('h')
        ),
        'type_of_unit': value.get('o'),
        'extent': value.get('n'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'privacy': indicator_map1.get(key[3]),
    }


@inspiremarc.over('information_relating_to_copyright_status', '^542[10_].')
@utils.for_each_value
@utils.filter_values
def information_relating_to_copyright_status(self, key, value):
    """Information Relating to Copyright Status."""
    indicator_map1 = {
        "#": "No information provided", "0": "Private", "1": "Not private"}
    return {
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'personal_creator': utils.force_list(
            value.get('a')
        ),
        'corporate_creator': utils.force_list(
            value.get('c')
        ),
        'personal_creator_death_date': utils.force_list(
            value.get('b')
        ),
        'copyright_holder_contact_information': value.get('e'),
        'copyright_holder': value.get('d'),
        'copyright_date': utils.force_list(
            value.get('g')
        ),
        'copyright_statement': value.get('f'),
        'publication_date': utils.force_list(
            value.get('i')
        ),
        'copyright_renewal_date': value.get('h'),
        'publisher': value.get('k'),
        'creation_date': utils.force_list(
            value.get('j')
        ),
        'publication_status': utils.force_list(
            value.get('m')
        ),
        'copyright_status': utils.force_list(
            value.get('l')
        ),
        'research_date': utils.force_list(
            value.get('o')
        ),
        'note': value.get('n'),
        'supplying_agency': utils.force_list(
            value.get('q')
        ),
        'country_of_publication_or_creation': value.get('p'),
        'source_of_information': utils.force_list(
            value.get('s')
        ),
        'jurisdiction_of_copyright_assessment': utils.force_list(
            value.get('r')
        ),
        'uniform_resource_identifier': value.get('u'),
        'privacy': indicator_map1.get(key[3]),
    }


@inspiremarc.over('location_of_other_archival_materials_note', '^544[10_].')
@utils.for_each_value
@utils.filter_values
def location_of_other_archival_materials_note(self, key, value):
    """Location of Other Archival Materials Note."""
    indicator_map1 = {"#": "No information provided",
                      "0": "Associated materials", "1": "Related materials"}
    return {
        'custodian': value.get('a'),
        'country': value.get('c'),
        'address': value.get('b'),
        'provenance': value.get('e'),
        'title': value.get('d'),
        'note': value.get('n'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'relationship': indicator_map1.get(key[3]),
    }


@inspiremarc.over('biographical_or_historical_data', '^545[10_].')
@utils.for_each_value
@utils.filter_values
def biographical_or_historical_data(self, key, value):
    """Biographical or Historical Data."""
    indicator_map1 = {
        "#": "No information provided",
        "0": "Biographical sketch",
        "1": "Administrative history"}
    return {
        'biographical_or_historical_data': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'expansion': utils.force_list(
            value.get('b')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'type_of_data': indicator_map1.get(key[3]),
    }


@inspiremarc.over('language_note', '^546..')
@utils.for_each_value
@utils.filter_values
def language_note(self, key, value):
    """Language Note."""
    return {
        'language_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'information_code_or_alphabet': value.get('b'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('former_title_complexity_note', '^547..')
@utils.for_each_value
@utils.filter_values
def former_title_complexity_note(self, key, value):
    """Former Title Complexity Note."""
    return {
        'former_title_complexity_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('issuing_body_note', '^550..')
@utils.for_each_value
@utils.filter_values
def issuing_body_note(self, key, value):
    """Issuing Body Note."""
    return {
        'issuing_body_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('entity_and_attribute_information_note', '^552..')
@utils.for_each_value
@utils.filter_values
def entity_and_attribute_information_note(self, key, value):
    """Entity and Attribute Information Note."""
    return {
        'entity_type_label': utils.force_list(
            value.get('a')
        ),
        'attribute_label': utils.force_list(
            value.get('c')
        ),
        'entity_type_definition_and_source': utils.force_list(
            value.get('b')
        ),
        'enumerated_domain_value': value.get('e'),
        'attribute_definition_and_source': utils.force_list(
            value.get('d')
        ),
        'range_domain_minimum_and_maximum': utils.force_list(
            value.get('g')
        ),
        'enumerated_domain_value_definition_and_source': value.get('f'),
        'unrepresentable_domain': utils.force_list(
            value.get('i')
        ),
        'codeset_name_and_source': utils.force_list(
            value.get('h')
        ),
        'beginning_and_ending_date_of_attribute_values': utils.force_list(
            value.get('k')
        ),
        'attribute_units_of_measurement_and_resolution': utils.force_list(
            value.get('j')
        ),
        'attribute_value_accuracy_explanation': utils.force_list(
            value.get('m')
        ),
        'attribute_value_accuracy': utils.force_list(
            value.get('l')
        ),
        'entity_and_attribute_overview': value.get('o'),
        'attribute_measurement_frequency': utils.force_list(
            value.get('n')
        ),
        'entity_and_attribute_detail_citation': value.get('p'),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_note': value.get('z'),
    }


@inspiremarc.over('cumulative_index_finding_aids_note', '^555[0_8].')
@utils.for_each_value
@utils.filter_values
def cumulative_index_finding_aids_note(self, key, value):
    """Cumulative Index/Finding Aids Note."""
    indicator_map1 = {
        "#": "Indexes",
        "0": "Finding aids",
        "8": "No display constant generated"}
    return {
        'cumulative_index_finding_aids_note': utils.force_list(
            value.get('a')
        ),
        'degree_of_control': utils.force_list(
            value.get('c')
        ),
        'availability_source': value.get('b'),
        'bibliographic_reference': utils.force_list(
            value.get('d')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('information_about_documentation_note', '^556[8_].')
@utils.for_each_value
@utils.filter_values
def information_about_documentation_note(self, key, value):
    """Information About Documentation Note."""
    indicator_map1 = {
        "#": "Documentation", "8": "No display constant generated"}
    return {
        'information_about_documentation_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'international_standard_book_number': value.get('z'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('ownership_and_custodial_history', '^561[10_].')
@utils.for_each_value
@utils.filter_values
def ownership_and_custodial_history(self, key, value):
    """Ownership and Custodial History."""
    indicator_map1 = {
        "#": "No information provided", "0": "Private", "1": "Not private"}
    return {
        'history': utils.force_list(
            value.get('a')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_resource_identifier': value.get('u'),
        'privacy': indicator_map1.get(key[3]),
    }


@inspiremarc.over('copy_and_version_identification_note', '^562..')
@utils.for_each_value
@utils.filter_values
def copy_and_version_identification_note(self, key, value):
    """Copy and Version Identification Note."""
    return {
        'identifying_markings': value.get('a'),
        'version_identification': value.get('c'),
        'copy_identification': value.get('b'),
        'number_of_copies': value.get('e'),
        'presentation_format': value.get('d'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('binding_information', '^563..')
@utils.for_each_value
@utils.filter_values
def binding_information(self, key, value):
    """Binding Information."""
    return {
        'binding_note': utils.force_list(
            value.get('a')
        ),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'uniform_resource_identifier': value.get('u'),
    }


@inspiremarc.over('case_file_characteristics_note', '^565[0_8].')
@utils.for_each_value
@utils.filter_values
def case_file_characteristics_note(self, key, value):
    """Case File Characteristics Note."""
    indicator_map1 = {
        "#": "File size",
        "0": "Case file characteristics",
        "8": "No display constant generated"}
    return {
        'number_of_cases_variables': utils.force_list(
            value.get('a')
        ),
        'unit_of_analysis': value.get('c'),
        'name_of_variable': value.get('b'),
        'filing_scheme_or_code': value.get('e'),
        'universe_of_data': value.get('d'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('methodology_note', '^567[8_].')
@utils.for_each_value
@utils.filter_values
def methodology_note(self, key, value):
    """Methodology Note."""
    indicator_map1 = {"#": "Methodology", "8": "No display constant generated"}
    return {
        'methodology_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('linking_entry_complexity_note', '^580..')
@utils.for_each_value
@utils.filter_values
def linking_entry_complexity_note(self, key, value):
    """Linking Entry Complexity Note."""
    return {
        'linking_entry_complexity_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('publications_about_described_materials_note', '^581[8_].')
@utils.for_each_value
@utils.filter_values
def publications_about_described_materials_note(self, key, value):
    """Publications About Described Materials Note."""
    indicator_map1 = {
        "#": "Publications", "8": "No display constant generated"}
    return {
        'publications_about_described_materials_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'international_standard_book_number': value.get('z'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('action_note', '^583[10_].')
@utils.for_each_value
@utils.filter_values
def action_note(self, key, value):
    """Action Note."""
    indicator_map1 = {
        "#": "No information provided", "0": "Private", "1": "Not private"}
    return {
        'action': utils.force_list(
            value.get('a')
        ),
        'nonpublic_note': value.get('x'),
        'time_date_of_action': value.get('c'),
        'action_identification': value.get('b'),
        'contingency_for_action': value.get('e'),
        'action_interval': value.get('d'),
        'authorization': value.get('f'),
        'method_of_action': value.get('i'),
        'jurisdiction': value.get('h'),
        'action_agent': value.get('k'),
        'site_of_action': value.get('j'),
        'status': value.get('l'),
        'type_of_unit': value.get('o'),
        'extent': value.get('n'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_term': utils.force_list(
            value.get('2')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'public_note': value.get('z'),
        'uniform_resource_identifier': value.get('u'),
        'privacy': indicator_map1.get(key[3]),
    }


@inspiremarc.over('accumulation_and_frequency_of_use_note', '^584..')
@utils.for_each_value
@utils.filter_values
def accumulation_and_frequency_of_use_note(self, key, value):
    """Accumulation and Frequency of Use Note."""
    return {
        'accumulation': value.get('a'),
        'frequency_of_use': value.get('b'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('exhibitions_note', '^585..')
@utils.for_each_value
@utils.filter_values
def exhibitions_note(self, key, value):
    """Exhibitions Note."""
    return {
        'exhibitions_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('awards_note', '^586[8_].')
@utils.for_each_value
@utils.filter_values
def awards_note(self, key, value):
    """Awards Note."""
    indicator_map1 = {"#": "Awards", "8": "No display constant generated"}
    return {
        'awards_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('source_of_description_note', '^588..')
@utils.for_each_value
@utils.filter_values
def source_of_description_note(self, key, value):
    """Source of Description Note."""
    return {
        'source_of_description_note': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'institution_to_which_field_applies': utils.force_list(
            value.get('5')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }
