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


@inspiremarc.over('physical_description', '^300..')
@utils.for_each_value
@utils.filter_values
def physical_description(self, key, value):
    """Physical Description."""
    return {
        'extent': value.get('a'),
        'dimensions': value.get('c'),
        'other_physical_details': utils.force_list(
            value.get('b')
        ),
        'accompanying_material': utils.force_list(
            value.get('e')
        ),
        'size_of_unit': value.get('g'),
        'type_of_unit': value.get('f'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('playing_time', '^306..')
@utils.filter_values
def playing_time(self, key, value):
    """Playing Time."""
    return {
        'playing_time': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('hours', '^307[8_].')
@utils.for_each_value
@utils.filter_values
def hours(self, key, value):
    """Hours, Etc.."""
    indicator_map1 = {"#": "Hours", "8": "No display constant generated"}
    return {
        'hours': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'additional_information': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'display_constant_controller': indicator_map1.get(key[3]),
    }


@inspiremarc.over('current_publication_frequency', '^310..')
@utils.filter_values
def current_publication_frequency(self, key, value):
    """Current Publication Frequency."""
    return {
        'current_publication_frequency': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'date_of_current_publication_frequency': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('former_publication_frequency', '^321..')
@utils.for_each_value
@utils.filter_values
def former_publication_frequency(self, key, value):
    """Former Publication Frequency."""
    return {
        'former_publication_frequency': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'dates_of_former_publication_frequency': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('content_type', '^336..')
@utils.for_each_value
@utils.filter_values
def content_type(self, key, value):
    """Content Type."""
    return {
        'content_type_term': value.get('a'),
        'content_type_code': value.get('b'),
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
    }


@inspiremarc.over('media_type', '^337..')
@utils.for_each_value
@utils.filter_values
def media_type(self, key, value):
    """Media Type."""
    return {
        'media_type_term': value.get('a'),
        'media_type_code': value.get('b'),
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
    }


@inspiremarc.over('carrier_type', '^338..')
@utils.for_each_value
@utils.filter_values
def carrier_type(self, key, value):
    """Carrier Type."""
    return {
        'carrier_type_term': value.get('a'),
        'carrier_type_code': value.get('b'),
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
    }


@inspiremarc.over('physical_medium', '^340..')
@utils.for_each_value
@utils.filter_values
def physical_medium(self, key, value):
    """Physical Medium."""
    return {
        'material_base_and_configuration': value.get('a'),
        'materials_applied_to_surface': value.get('c'),
        'dimensions': value.get('b'),
        'support': value.get('e'),
        'information_recording_technique': value.get('d'),
        'production_rate_ratio': value.get('f'),
        'technical_specifications_of_medium': value.get('i'),
        'location_within_medium': value.get('h'),
        'layout': value.get('k'),
        'generation': value.get('j'),
        'book_format': value.get('m'),
        'polarity': value.get('o'),
        'font_size': value.get('n'),
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
    }


@inspiremarc.over('geospatial_reference_data', '^342[10_][_103254768]')
@utils.for_each_value
@utils.filter_values
def geospatial_reference_data(self, key, value):
    """Geospatial Reference Data."""
    indicator_map1 = {
        "0": "Horizontal coordinate system", "1": "Vertical coordinate system"}
    indicator_map2 = {"0": "Geographic", "1": "Map projection", "2": "Grid coordinate system", "3": "Local planar",
                      "4": "Local", "5": "Geodetic model", "6": "Altitude", "7": "Method specified in $2", "8": "Depth"}
    return {
        'reference_method_used': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'name': utils.force_list(
            value.get('a')
        ),
        'latitude_resolution': utils.force_list(
            value.get('c')
        ),
        'coordinate_units_or_distance_units': utils.force_list(
            value.get('b')
        ),
        'standard_parallel_or_oblique_line_latitude': value.get('e'),
        'longitude_resolution': utils.force_list(
            value.get('d')
        ),
        'longitude_of_central_meridian_or_projection_center': utils.force_list(
            value.get('g')
        ),
        'oblique_line_longitude': value.get('f'),
        'false_easting': utils.force_list(
            value.get('i')
        ),
        'latitude_of_projection_center_or_projection_origin': utils.force_list(
            value.get('h')
        ),
        'scale_factor': utils.force_list(
            value.get('k')
        ),
        'false_northing': utils.force_list(
            value.get('j')
        ),
        'azimuthal_angle': utils.force_list(
            value.get('m')
        ),
        'height_of_perspective_point_above_surface': utils.force_list(
            value.get('l')
        ),
        'landsat_number_and_path_number': utils.force_list(
            value.get('o')
        ),
        'azimuth_measure_point_longitude_or_straight_vertical_longitude_from_pole': utils.force_list(
            value.get('n')
        ),
        'ellipsoid_name': utils.force_list(
            value.get('q')
        ),
        'zone_identifier': utils.force_list(
            value.get('p')
        ),
        'denominator_of_flattening_ratio': utils.force_list(
            value.get('s')
        ),
        'semi_major_axis': utils.force_list(
            value.get('r')
        ),
        'vertical_encoding_method': utils.force_list(
            value.get('u')
        ),
        'vertical_resolution': utils.force_list(
            value.get('t')
        ),
        'local_planar_or_local_georeference_information': utils.force_list(
            value.get('w')
        ),
        'local_planar_local_or_other_projection_or_grid_description': utils.force_list(
            value.get('v')
        ),
        'geospatial_reference_dimension': indicator_map1.get(key[3]),
        'geospatial_reference_method': indicator_map2.get(key[4]),
    }


@inspiremarc.over('planar_coordinate_data', '^343..')
@utils.for_each_value
@utils.filter_values
def planar_coordinate_data(self, key, value):
    """Planar Coordinate Data."""
    return {
        'planar_coordinate_encoding_method': utils.force_list(
            value.get('a')
        ),
        'abscissa_resolution': utils.force_list(
            value.get('c')
        ),
        'planar_distance_units': utils.force_list(
            value.get('b')
        ),
        'distance_resolution': utils.force_list(
            value.get('e')
        ),
        'ordinate_resolution': utils.force_list(
            value.get('d')
        ),
        'bearing_units': utils.force_list(
            value.get('g')
        ),
        'bearing_resolution': utils.force_list(
            value.get('f')
        ),
        'bearing_reference_meridian': utils.force_list(
            value.get('i')
        ),
        'bearing_reference_direction': utils.force_list(
            value.get('h')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('sound_characteristics', '^344..')
@utils.for_each_value
@utils.filter_values
def sound_characteristics(self, key, value):
    """Sound Characteristics."""
    return {
        'type_of_recording': value.get('a'),
        'playing_speed': value.get('c'),
        'recording_medium': value.get('b'),
        'track_configuration': value.get('e'),
        'groove_characteristic': value.get('d'),
        'configuration_of_playback_channels': value.get('g'),
        'tape_configuration': value.get('f'),
        'special_playback_characteristics': value.get('h'),
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
    }


@inspiremarc.over('projection_characteristics_of_moving_image', '^345..')
@utils.for_each_value
@utils.filter_values
def projection_characteristics_of_moving_image(self, key, value):
    """Projection Characteristics of Moving Image."""
    return {
        'presentation_format': value.get('a'),
        'projection_speed': value.get('b'),
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
    }


@inspiremarc.over('video_characteristics', '^346..')
@utils.for_each_value
@utils.filter_values
def video_characteristics(self, key, value):
    """Video Characteristics."""
    return {
        'video_format': value.get('a'),
        'broadcast_standard': value.get('b'),
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
    }


@inspiremarc.over('digital_file_characteristics', '^347..')
@utils.for_each_value
@utils.filter_values
def digital_file_characteristics(self, key, value):
    """Digital File Characteristics."""
    return {
        'file_type': value.get('a'),
        'file_size': value.get('c'),
        'encoding_format': value.get('b'),
        'regional_encoding': value.get('e'),
        'resolution': value.get('d'),
        'transmission_speed': value.get('f'),
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
    }


@inspiremarc.over('organization_and_arrangement_of_materials', '^351..')
@utils.for_each_value
@utils.filter_values
def organization_and_arrangement_of_materials(self, key, value):
    """Organization and Arrangement of Materials."""
    return {
        'organization': value.get('a'),
        'hierarchical_level': utils.force_list(
            value.get('c')
        ),
        'arrangement': value.get('b'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('digital_graphic_representation', '^352..')
@utils.for_each_value
@utils.filter_values
def digital_graphic_representation(self, key, value):
    """Digital Graphic Representation."""
    return {
        'direct_reference_method': utils.force_list(
            value.get('a')
        ),
        'object_count': value.get('c'),
        'object_type': value.get('b'),
        'column_count': utils.force_list(
            value.get('e')
        ),
        'row_count': utils.force_list(
            value.get('d')
        ),
        'vpf_topology_level': utils.force_list(
            value.get('g')
        ),
        'vertical_count': utils.force_list(
            value.get('f')
        ),
        'indirect_reference_description': utils.force_list(
            value.get('i')
        ),
        'format_of_the_digital_image': utils.force_list(
            value.get('q')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('security_classification_control', '^355[1032548_].')
@utils.for_each_value
@utils.filter_values
def security_classification_control(self, key, value):
    """Security Classification Control."""
    indicator_map1 = {"0": "Document", "1": "Title", "2": "Abstract", "3":
                      "Contents note", "4": "Author", "5": "Record", "8": "None of the above"}
    return {
        'security_classification': utils.force_list(
            value.get('a')
        ),
        'external_dissemination_information': value.get('c'),
        'handling_instructions': value.get('b'),
        'classification_system': utils.force_list(
            value.get('e')
        ),
        'downgrading_or_declassification_event': utils.force_list(
            value.get('d')
        ),
        'downgrading_date': utils.force_list(
            value.get('g')
        ),
        'country_of_origin_code': utils.force_list(
            value.get('f')
        ),
        'declassification_date': utils.force_list(
            value.get('h')
        ),
        'authorization': value.get('j'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'controlled_element': indicator_map1.get(key[3]),
    }


@inspiremarc.over('originator_dissemination_control', '^357..')
@utils.filter_values
def originator_dissemination_control(self, key, value):
    """Originator Dissemination Control."""
    return {
        'originator_control_term': utils.force_list(
            value.get('a')
        ),
        'authorized_recipients_of_material': value.get('c'),
        'originating_agency': value.get('b'),
        'other_restrictions': value.get('g'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over(
    'dates_of_publication_and_or_sequential_designation', '^362[10_].')
@utils.for_each_value
@utils.filter_values
def dates_of_publication_and_or_sequential_designation(self, key, value):
    """Dates of Publication and/or Sequential Designation."""
    indicator_map1 = {"0": "Formatted style", "1": "Unformatted note"}
    return {
        'dates_of_publication_and_or_sequential_designation': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'source_of_information': utils.force_list(
            value.get('z')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'format_of_date': indicator_map1.get(key[3]),
    }


@inspiremarc.over('normalized_date_and_sequential_designation', '^363[10_][10_]')
@utils.for_each_value
@utils.filter_values
def normalized_date_and_sequential_designation(self, key, value):
    """Normalized Date and Sequential Designation."""
    indicator_map1 = {"#": "No information provided",
                      "0": "Starting information", "1": "Ending information"}
    indicator_map2 = {"#": "Not specified", "0": "Closed", "1": "Open"}
    return {
        'first_level_of_enumeration': utils.force_list(
            value.get('a')
        ),
        'nonpublic_note': value.get('x'),
        'third_level_of_enumeration': utils.force_list(
            value.get('c')
        ),
        'second_level_of_enumeration': utils.force_list(
            value.get('b')
        ),
        'fifth_level_of_enumeration': utils.force_list(
            value.get('e')
        ),
        'fourth_level_of_enumeration': utils.force_list(
            value.get('d')
        ),
        'alternative_numbering_scheme_first_level_of_enumeration': utils.force_list(
            value.get('g')
        ),
        'sixth_level_of_enumeration': utils.force_list(
            value.get('f')
        ),
        'first_level_of_chronology': utils.force_list(
            value.get('i')
        ),
        'alternative_numbering_scheme_second_level_of_enumeration': utils.force_list(
            value.get('h')
        ),
        'third_level_of_chronology': utils.force_list(
            value.get('k')
        ),
        'second_level_of_chronology': utils.force_list(
            value.get('j')
        ),
        'alternative_numbering_scheme_chronology': utils.force_list(
            value.get('m')
        ),
        'fourth_level_of_chronology': utils.force_list(
            value.get('l')
        ),
        'first_level_textual_designation': utils.force_list(
            value.get('u')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': utils.force_list(
            value.get('8')
        ),
        'public_note': value.get('z'),
        'first_level_of_chronology_issuance': utils.force_list(
            value.get('v')
        ),
        'start_end_designator': indicator_map1.get(key[3]),
        'state_of_issuance': indicator_map2.get(key[4]),
    }


@inspiremarc.over('trade_price', '^365..')
@utils.for_each_value
@utils.filter_values
def trade_price(self, key, value):
    """Trade Price."""
    return {
        'price_type_code': utils.force_list(
            value.get('a')
        ),
        'currency_code': utils.force_list(
            value.get('c')
        ),
        'price_amount': utils.force_list(
            value.get('b')
        ),
        'price_note': utils.force_list(
            value.get('e')
        ),
        'unit_of_pricing': utils.force_list(
            value.get('d')
        ),
        'price_effective_until': utils.force_list(
            value.get('g')
        ),
        'price_effective_from': utils.force_list(
            value.get('f')
        ),
        'tax_rate_2': utils.force_list(
            value.get('i')
        ),
        'tax_rate_1': utils.force_list(
            value.get('h')
        ),
        'marc_country_code': utils.force_list(
            value.get('k')
        ),
        'iso_country_code': utils.force_list(
            value.get('j')
        ),
        'identification_of_pricing_entity': utils.force_list(
            value.get('m')
        ),
        'source_of_price_type_code': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('trade_availability_information', '^366..')
@utils.for_each_value
@utils.filter_values
def trade_availability_information(self, key, value):
    """Trade Availability Information."""
    return {
        'publishers_compressed_title_identification': utils.force_list(
            value.get('a')
        ),
        'availability_status_code': utils.force_list(
            value.get('c')
        ),
        'detailed_date_of_publication': utils.force_list(
            value.get('b')
        ),
        'note': utils.force_list(
            value.get('e')
        ),
        'expected_next_availability_date': utils.force_list(
            value.get('d')
        ),
        'date_made_out_of_print': utils.force_list(
            value.get('g')
        ),
        'publisher_s_discount_category': utils.force_list(
            value.get('f')
        ),
        'marc_country_code': utils.force_list(
            value.get('k')
        ),
        'iso_country_code': utils.force_list(
            value.get('j')
        ),
        'identification_of_agency': utils.force_list(
            value.get('m')
        ),
        'source_of_availability_status_code': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('associated_language', '^377..')
@utils.for_each_value
@utils.filter_values
def associated_language(self, key, value):
    """Associated Language."""
    return {
        'language_code': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'source': utils.force_list(
            value.get('2')
        ),
        'language_term': value.get('l'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('form_of_work', '^380..')
@utils.for_each_value
@utils.filter_values
def form_of_work(self, key, value):
    """Form of Work."""
    return {
        'form_of_work': value.get('a'),
        'record_control_number': value.get('0'),
        'source_of_term': utils.force_list(
            value.get('2')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over(
    'other_distinguishing_characteristics_of_work_or_expression', '^381..')
@utils.for_each_value
@utils.filter_values
def other_distinguishing_characteristics_of_work_or_expression(
        self, key, value):
    """Other Distinguishing Characteristics of Work or Expression."""
    return {
        'other_distinguishing_characteristic': value.get('a'),
        'source_of_information': value.get('v'),
        'record_control_number': value.get('0'),
        'source_of_term': utils.force_list(
            value.get('2')
        ),
        'uniform_resource_identifier': value.get('u'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('medium_of_performance', '^382[10_][10_]')
@utils.for_each_value
@utils.filter_values
def medium_of_performance(self, key, value):
    """Medium of Performance."""
    indicator_map1 = {"#": "No information provided", "0":
                      "Medium of performance", "1": "Partial medium of performance"}
    indicator_map2 = {"#": "No information provided",
                      "0": "Not intended for access", "1": "Intended for access"}
    return {
        'medium_of_performance': value.get('a'),
        'soloist': value.get('b'),
        'doubling_instrument': value.get('d'),
        'alternative_medium_of_performance': value.get('p'),
        'note': value.get('v'),
        'number_of_performers_of_the_same_medium': value.get('n'),
        'authority_record_control_number_or_standard_number': value.get('0'),
        'total_number_of_performers': value.get('s'),
        'source_of_term': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'display_constant_controller': indicator_map1.get(key[3]),
        'access_control': indicator_map2.get(key[4]),
    }


@inspiremarc.over('numeric_designation_of_musical_work', '^383..')
@utils.for_each_value
@utils.filter_values
def numeric_designation_of_musical_work(self, key, value):
    """Numeric Designation of Musical Work."""
    return {
        'serial_number': value.get('a'),
        'thematic_index_number': value.get('c'),
        'opus_number': value.get('b'),
        'publisher_associated_with_opus_number': utils.force_list(
            value.get('e')
        ),
        'thematic_index_code': utils.force_list(
            value.get('d')
        ),
        'source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('key', '^384[10_].')
@utils.filter_values
def key(self, key, value):
    """Key."""
    indicator_map1 = {"#": "Relationship to original unknown ",
                      "0": "Original key ", "1": "Transposed key "}
    return {
        'key': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'key_type': indicator_map1.get(key[3]),
    }


@inspiremarc.over('audience_characteristics', '^385..')
@utils.for_each_value
@utils.filter_values
def audience_characteristics(self, key, value):
    """Audience Characteristics."""
    return {
        'audience_term': value.get('a'),
        'audience_code': value.get('b'),
        'demographic_group_term': utils.force_list(
            value.get('m')
        ),
        'demographic_group_code': utils.force_list(
            value.get('n')
        ),
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
    }


@inspiremarc.over('creator_contributor_characteristics', '^386..')
@utils.for_each_value
@utils.filter_values
def creator_contributor_characteristics(self, key, value):
    """Creator/Contributor Characteristics."""
    return {
        'creator_contributor_term': value.get('a'),
        'creator_contributor_code': value.get('b'),
        'demographic_group_term': utils.force_list(
            value.get('m')
        ),
        'demographic_group_code': utils.force_list(
            value.get('n')
        ),
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
    }
