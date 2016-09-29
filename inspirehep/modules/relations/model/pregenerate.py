# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from inspirehep.config import INSPIRE_CATEGORIES, INSPIRE_RANK_TYPES

from inspirehep.modules.relations.model.constants import (
    CONTINENTS,
    COUNTRIES_TO_CONTINETS,
    COUNTRY_CODE_SCHEMA
    )
from inspirehep.modules.relations.graph_representation import (
    create_graph_dict,
    get_central_node,
    render_graph_dict
    )
from inspirehep.modules.relations.model.nodes import (
    CountryNode,
    ContinentNode,
    ResearchFieldNode,
    ScientificRankNode
    )
from inspirehep.modules.relations.model.relations import (
    LOCATED_IN
    )
from inspirehep.modules.relations.model_updaters import (
    add_outgoing_relation,
    set_uid,
    set_property_of_central_node
    )

COUNTRIES_TO_CREATE = [
    {
        'country_code': country_code,
        'details': COUNTRIES_TO_CONTINETS[country_code]
    }
    for country_code in COUNTRY_CODE_SCHEMA['enum']
    if country_code in COUNTRIES_TO_CONTINETS
]
# TODO: add ~30 missing country-to-continent mappings


def pregenerate_research_fields():
    for category in INSPIRE_CATEGORIES:
        model = create_graph_dict(central_node_type=ResearchFieldNode)
        set_uid(model,
                uid=ResearchFieldNode.generate_uid(category))
        set_property_of_central_node(model, 'name', category)
        render_graph_dict(model)
        yield model


def pregenerate_scientific_ranks():
    for rank_name in INSPIRE_RANK_TYPES.keys():
        model = create_graph_dict(central_node_type=ScientificRankNode)
        set_uid(model,
                uid=ScientificRankNode.generate_uid(rank_name))
        set_property_of_central_node(model, 'name', rank_name)
        render_graph_dict(model)
        yield model


def pregenerate_countries_and_continents():
    continents = {}
    for continent_name in CONTINENTS:
        continent_model = create_graph_dict(central_node_type=ContinentNode)
        set_uid(continent_model,
                uid=ContinentNode.generate_uid(continent_name))
        set_property_of_central_node(continent_model, 'name', continent_name)
        continents[continent_name] = get_central_node(continent_model)
        render_graph_dict(continent_model)
        yield continent_model

    for country in COUNTRIES_TO_CREATE:
        country_model = create_graph_dict(central_node_type=CountryNode)
        set_uid(country_model, uid=CountryNode.generate_uid(
            country['country_code']))
        set_property_of_central_node(country_model,
                                     'name', country['details']['name'])
        for continent_name in country['details']['continent']:
            continent = continents[continent_name]
            add_outgoing_relation(country_model, LOCATED_IN, continent)

        render_graph_dict(country_model)
        yield country_model


def pregenerate_graph():
    for rf in pregenerate_research_fields():
        yield rf

    for sr in pregenerate_scientific_ranks():
        yield sr

    for cc in pregenerate_countries_and_continents():
        yield cc
