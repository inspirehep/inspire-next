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

from inspirehep.dojson.utils import get_recid_from_ref

from inspirehep.modules.relations.graph_representation import (
        GraphModelBuilder,
        make_node
)
from inspirehep.modules.relations.model_updaters import (
    add_outgoing_relation,
    set_property_of_central_node,
    set_uid
)
from inspirehep.modules.relations.model.nodes import InstitutionNode
from inspirehep.modules.relations.model.relations import (
        SUCCESSOR_OF,
        CHILD_OF,
        SUPERSEDES,
        SOMEHOW_RELATED_TO
)


institutions = GraphModelBuilder(central_node_type=InstitutionNode)


@institutions.element_processor('control_number')
def recid(model, element):
    set_property_of_central_node(model,
                                 'recid', str(element))

    set_uid(model,
            uid=InstitutionNode.generate_uid(recid=element))


@institutions.element_processor('related_institutes',
                                musts=['record', 'relation_type'])
def related_institutes(model, element):
    JSON_RELATION_TO_GRAPH_RELATION = {
            "predecessor": SUCCESSOR_OF,
            "parent": CHILD_OF,
            "superseded": SUPERSEDES,
            "other": SOMEHOW_RELATED_TO
    }

    relation = JSON_RELATION_TO_GRAPH_RELATION.get(element['relation_type'])

    if relation:
        related_institution_recid = get_recid_from_ref(element['record'])
        related_institution = make_node(InstitutionNode,
                                        recid=related_institution_recid)

        add_outgoing_relation(model, relation, related_institution)
