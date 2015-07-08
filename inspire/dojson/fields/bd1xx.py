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


@inspiremarc.over('authors', '^[17]00[103_].')
# @utils.filter_values
def authors(self, key, value):
    """Main Entry-Personal Name."""
    value = utils.force_list(value)

    def get_value(value):
            return {
                'full_name': value.get('a'),
                'relator_term': value.get('e'),
                'alternative_name': value.get('q'),
                'INSPIRE_id': value.get('i'),
                'external_id': value.get('j'),
                'e_mail': value.get('m'),
                'affiliation': utils.force_list(
                    value.get('u')
                ),
            }

    authors = self.get('authors', [])

    if key.startswith('100'):
        authors.insert(0, get_value(value[0]))
    else:
        for single_value in value:
            authors.append(get_value(single_value))

    return authors


@inspiremarc.over('corporate_author', '^110[10_2].')
@utils.filter_values
def corporate_author(self, key, value):
    """Main Entry-Corporate Name."""
    return {
        'corporate_author': value.get('a'),
    }


@inspiremarc.over('institution', '^110..')
@utils.filter_values
def institution(self, key, value):
    """Institution info."""
    return {
        'name': value.get('a'),
        'department': value.get('b'),
        'new_name': value.get('t'),
        'affiliation': value.get('u'),
        'obsolete_icn': value.get('x'),
    }
