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


@inspiremarc.over('holding_institution', '^850..')
@utils.for_each_value
@utils.filter_values
def holding_institution(self, key, value):
    """Holding Institution."""
    return {
        'holding_institution': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('location', '^852[_103254768][10_2]')
@utils.for_each_value
@utils.filter_values
def location(self, key, value):
    """Location."""
    indicator_map1 = {
        "#": "No information provided",
        "0": "Library of Congress classification",
        "1": "Dewey Decimal classification",
        "2": "National Library of Medicine classification",
        "3": "Superintendent of Documents classification",
        "4": "Shelving control number",
        "5": "Title",
        "6": "Shelved separately",
        "7": "Source specified in subfield $2",
        "8": "Other scheme"}
    indicator_map2 = {
        "#": "No information provided",
        "0": "Not enumeration",
        "1": "Primary enumeration",
        "2": "Alternative enumeration"}
    return {
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'source_of_classification_or_shelving_scheme': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'sequence_number': utils.force_list(
            value.get('8')
        ),
        'location': utils.force_list(
            value.get('a')
        ),
        'shelving_location': value.get('c'),
        'sublocation_or_collection': value.get('b'),
        'address': value.get('e'),
        'former_shelving_location': value.get('d'),
        'non_coded_location_qualifier': value.get('g'),
        'coded_location_qualifier': value.get('f'),
        'item_part': value.get('i'),
        'classification_part': utils.force_list(
            value.get('h')
        ),
        'call_number_prefix': value.get('k'),
        'shelving_control_number': utils.force_list(
            value.get('j')
        ),
        'call_number_suffix': value.get('m'),
        'shelving_form_of_title': utils.force_list(
            value.get('l')
        ),
        'country_code': utils.force_list(
            value.get('n')
        ),
        'piece_physical_condition': utils.force_list(
            value.get('q')
        ),
        'piece_designation': utils.force_list(
            value.get('p')
        ),
        'copyright_article_fee_code': value.get('s'),
        'uniform_resource_identifier': value.get('u'),
        'copy_number': utils.force_list(
            value.get('t')
        ),
        'nonpublic_note': value.get('x'),
        'public_note': value.get('z'),
        'shelving_scheme': indicator_map1.get(key[3]),
        'shelving_order': indicator_map2.get(key[4]),
    }


@inspiremarc.over('electronic_location_and_access', '^856.[10_28]')
@utils.for_each_value
@utils.filter_values
def electronic_location_and_access(self, key, value):
    """Electronic Location and Access."""
    indicator_map2 = {
        "#": "No information provided",
        "0": "Resource",
        "1": "Version of resource",
        "2": "Related resource",
        "8": "No display constant generated"}
    return {
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'access_method': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'host_name': value.get('a'),
        'compression_information': value.get('c'),
        'access_number': value.get('b'),
        'path': value.get('d'),
        'electronic_name': value.get('f'),
        'instruction': value.get('i'),
        'processor_of_request': utils.force_list(
            value.get('h')
        ),
        'password': utils.force_list(
            value.get('k')
        ),
        'bits_per_second': utils.force_list(
            value.get('j')
        ),
        'contact_for_access_assistance': value.get('m'),
        'logon': utils.force_list(
            value.get('l')
        ),
        'operating_system': utils.force_list(
            value.get('o')
        ),
        'name_of_location_of_host': utils.force_list(
            value.get('n')
        ),
        'electronic_format_type': utils.force_list(
            value.get('q')
        ),
        'port': utils.force_list(
            value.get('p')
        ),
        'file_size': value.get('s'),
        'settings': utils.force_list(
            value.get('r')
        ),
        'uniform_resource_identifier': value.get('u'),
        'terminal_emulation': value.get('t'),
        'record_control_number': value.get('w'),
        'hours_access_method_available': value.get('v'),
        'link_text': value.get('y'),
        'nonpublic_note': value.get('x'),
        'public_note': value.get('z'),
        'relationship': indicator_map2.get(key[4]),
    }


@inspiremarc.over('replacement_record_information', '^882..')
@utils.filter_values
def replacement_record_information(self, key, value):
    """Replacement Record Information."""
    return {
        'replacement_title': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'explanatory_text': value.get('i'),
        'replacement_bibliographic_record_control_number': value.get('w'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('machine_generated_metadata_provenance', '^883[10_].')
@utils.for_each_value
@utils.filter_values
def machine_generated_metadata_provenance(self, key, value):
    """Machine-generated Metadata Provenance."""
    indicator_map1 = {
        "#": "No information provided/not applicable",
        "0": "Fully machine-generated",
        "1": "Partially machine-generated"}
    return {
        'generation_process': utils.force_list(
            value.get('a')
        ),
        'confidence_value': utils.force_list(
            value.get('c')
        ),
        'generation_date': utils.force_list(
            value.get('d')
        ),
        'generation_agency': utils.force_list(
            value.get('q')
        ),
        'authority_record_control_number_or_standard_number': value.get('0'),
        'uniform_resource_identifier': utils.force_list(
            value.get('u')
        ),
        'bibliographic_record_control_number': value.get('w'),
        'validity_end_date': utils.force_list(
            value.get('x')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'method_of_machine_assignment': indicator_map1.get(key[3]),
    }


@inspiremarc.over('non_marc_information_field', '^887..')
@utils.for_each_value
@utils.filter_values
def non_marc_information_field(self, key, value):
    """Non-MARC Information Field."""
    return {
        'content_of_non_marc_field': utils.force_list(
            value.get('a')
        ),
        'source_of_data': utils.force_list(
            value.get('2')
        ),
    }
