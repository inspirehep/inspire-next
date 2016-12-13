# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Record enhancers for suggester fields."""

from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_value


def populate_experiment_name_suggester(json):
    experiment_names = get_value(json, 'experiment_names.title')
    title_variants = force_force_list(
        get_value(json, 'title_variants.title'))

    json.update({
        'experiment_suggest': {
            'input': experiment_names + title_variants,
            'output': experiment_names[0],
            'payload': {'$ref': get_value(json, 'self.$ref')},
        },
    })


def populate_abstract_suggester(json):
    abstracts = json.get('abstracts', [])
    for abstract in abstracts:
        source = abstract.get('source')
        if source:
            abstract.update({
                'abstract_source_suggest': {
                    'input': source,
                    'output': source,
                },
            })
