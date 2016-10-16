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

from inspirehep.modules.relations.graph_representation import (
        GraphModelBuilder,
        make_node
)
from inspirehep.modules.relations.model.nodes import (
    ConferenceNode,
    ConferenceSeriesNode
    )
from inspirehep.modules.relations.model.relations import PART_OF
from inspirehep.modules.relations.model_updaters import (
    add_outgoing_relation,
    set_property_of_central_node,
    set_uid
    )
from inspirehep.modules.relations.utils import clear_string


conferences = GraphModelBuilder(central_node_type=ConferenceNode)

@conferences.element_processor('control_number')
def recid(model, element):
    set_property_of_central_node(model,
                                 'recid', str(element))
    set_uid(model,
            uid=ConferenceNode.generate_uid(recid=element))


@conferences.element_processor('series', musts=['name'])
def conference_series(model, element):
    name = clear_string(element['name'])
    series_number = element.get('number')

    series_uid = ConferenceSeriesNode.generate_uid(name=name)
    conference_series = make_node(ConferenceSeriesNode, uid=series_uid)

    add_outgoing_relation(model, PART_OF, conference_series,
                          properties={'series_number': series_number})
