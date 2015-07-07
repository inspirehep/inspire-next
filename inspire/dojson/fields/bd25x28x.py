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


@inspiremarc.over('edition_statement', '^250..')
@utils.for_each_value
@utils.filter_values
def edition_statement(self, key, value):
    """Edition Statement."""
    return {
        'edition_statement': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'remainder_of_edition_statement': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('musical_presentation_statement', '^254..')
@utils.filter_values
def musical_presentation_statement(self, key, value):
    """Musical Presentation Statement."""
    return {
        'musical_presentation_statement': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('cartographic_mathematical_data', '^255..')
@utils.for_each_value
@utils.filter_values
def cartographic_mathematical_data(self, key, value):
    """Cartographic Mathematical Data."""
    return {
        'statement_of_scale': utils.force_list(
            value.get('a')
        ),
        'statement_of_coordinates': utils.force_list(
            value.get('c')
        ),
        'statement_of_projection': utils.force_list(
            value.get('b')
        ),
        'statement_of_equinox': utils.force_list(
            value.get('e')
        ),
        'statement_of_zone': utils.force_list(
            value.get('d')
        ),
        'exclusion_g_ring_coordinate_pairs': utils.force_list(
            value.get('g')
        ),
        'outer_g_ring_coordinate_pairs': utils.force_list(
            value.get('f')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('computer_file_characteristics', '^256..')
@utils.filter_values
def computer_file_characteristics(self, key, value):
    """Computer File Characteristics."""
    return {
        'computer_file_characteristics': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('country_of_producing_entity', '^257..')
@utils.for_each_value
@utils.filter_values
def country_of_producing_entity(self, key, value):
    """Country of Producing Entity."""
    return {
        'country_of_producing_entity': value.get('a'),
        'field_link_and_sequence_number': value.get('8'),
        'source': utils.force_list(
            value.get('2')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('philatelic_issue_data', '^258..')
@utils.for_each_value
@utils.filter_values
def philatelic_issue_data(self, key, value):
    """Philatelic Issue Data."""
    return {
        'issuing_jurisdiction': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'denomination': utils.force_list(
            value.get('b')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over('publication_distribution_imprint', '^260[_23].')
@utils.for_each_value
@utils.filter_values
def publication_distribution_imprint(self, key, value):
    """Publication, Distribution, etc. (Imprint)."""
    indicator_map1 = {
        "#": "Not applicable/No information provided/Earliest available publisher",
        "2": "Intervening publisher",
        "3": "Current/latest publisher"}
    return {
        'place_of_publication_distribution': value.get('a'),
        'date_of_publication_distribution': value.get('c'),
        'name_of_publisher_distributor': value.get('b'),
        'place_of_manufacture': value.get('e'),
        'date_of_manufacture': value.get('g'),
        'manufacturer': value.get('f'),
        'materials_specified': utils.force_list(
            value.get('3')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'sequence_of_publishing_statements': indicator_map1.get(key[3]),
    }


@inspiremarc.over('imprint_statement_for_films_pre_aacr_1_revised', '^261..')
@utils.filter_values
def imprint_statement_for_films_pre_aacr_1_revised(self, key, value):
    """Imprint Statement for Films (Pre-AACR 1 Revised)."""
    return {
        'producing_company': value.get('a'),
        'releasing_company': value.get('b'),
        'contractual_producer': value.get('e'),
        'date_of_production_release': value.get('d'),
        'place_of_production_release': value.get('f'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('imprint_statement_for_sound_recordings_pre_aacr_1', '^262..')
@utils.filter_values
def imprint_statement_for_sound_recordings_pre_aacr_1(self, key, value):
    """Imprint Statement for Sound Recordings (Pre-AACR 1)."""
    return {
        'place_of_production_release': utils.force_list(
            value.get('a')
        ),
        'date_of_production_release': utils.force_list(
            value.get('c')
        ),
        'publisher_or_trade_name': utils.force_list(
            value.get('b')
        ),
        'serial_identification': utils.force_list(
            value.get('k')
        ),
        'matrix_and_or_take_number': utils.force_list(
            value.get('l')
        ),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
    }


@inspiremarc.over('projected_publication_date', '^263..')
@utils.filter_values
def projected_publication_date(self, key, value):
    """Projected Publication Date."""
    return {
        'projected_publication_date': utils.force_list(
            value.get('a')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'linkage': utils.force_list(
            value.get('6')
        ),
    }


@inspiremarc.over(
    'production_publication_distribution_manufacture_and_copyright_notice',
    '^264[_23][10324_]')
@utils.for_each_value
@utils.filter_values
def production_publication_distribution_manufacture_and_copyright_notice(
        self, key, value):
    """Production, Publication, Distribution, Manufacture, and Copyright Notice."""
    indicator_map1 = {"#": "Not applicable/No information provided/Earliest",
                      "2": "Intervening", "3": "Current/latest"}
    indicator_map2 = {
        "0": "Production",
        "1": "Publication",
        "2": "Distribution",
        "3": "Manufacture",
        "4": "Copyright notice date"}
    return {
        'place_of_production_publication_distribution_manufacture': value.get('a'),
        'date_of_production_publication_distribution_manufacture_or_copyright_notice': value.get('c'),
        'name_of_producer_publisher_distributor_manufacturer': value.get('b'),
        'materials_specified': utils.force_list(
            value.get('3')),
        'linkage': utils.force_list(
            value.get('6')),
        'field_link_and_sequence_number': value.get('8'),
        'sequence_of_statements': indicator_map1.get(
            key[3]),
        'function_of_entity': indicator_map2.get(
            key[4]),
    }


@inspiremarc.over('address', '^270[1_2].')
@utils.for_each_value
@utils.filter_values
def address(self, key, value):
    """Address."""
    indicator_map1 = {
        "#": "No level specified", "1": "Primary", "2": "Secondary"}
    return {
        'address': value.get('a'),
        'state_or_province': utils.force_list(
            value.get('c')
        ),
        'city': utils.force_list(
            value.get('b')
        ),
        'postal_code': utils.force_list(
            value.get('e')
        ),
        'country': utils.force_list(
            value.get('d')
        ),
        'attention_name': utils.force_list(
            value.get('g')
        ),
        'terms_preceding_attention_name': utils.force_list(
            value.get('f')
        ),
        'type_of_address': utils.force_list(
            value.get('i')
        ),
        'attention_position': utils.force_list(
            value.get('h')
        ),
        'telephone_number': value.get('k'),
        'specialized_telephone_number': value.get('j'),
        'electronic_mail_address': value.get('m'),
        'fax_number': value.get('l'),
        'tdd_or_tty_number': value.get('n'),
        'title_of_contact_person': value.get('q'),
        'contact_person': value.get('p'),
        'hours': value.get('r'),
        'relator_code': value.get('4'),
        'linkage': utils.force_list(
            value.get('6')
        ),
        'field_link_and_sequence_number': value.get('8'),
        'public_note': value.get('z'),
        'level': indicator_map1.get(key[3]),
    }
