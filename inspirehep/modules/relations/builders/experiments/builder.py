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

from inspirehep.modules.relations.graph_representation import (make_node,
                                                     GraphModelBuilder
                                                     )
from inspirehep.modules.relations.model.nodes import (
    ExperimentNode,
    InstitutionNode
    )
from inspirehep.modules.relations.model.relations import AFFILIATED_WITH
from inspirehep.modules.relations.model_updaters import (
    add_outgoing_relation,
    set_property_of_central_node,
    set_uid
    )


experiments = GraphModelBuilder(central_node_type=ExperimentNode)


@experiments.element_processor('control_number')
def recid(model, element):
    set_property_of_central_node(model,
                                 'recid', str(element))

    set_uid(model,
            uid=ExperimentNode.generate_uid(recid=element))


@experiments.element_processor('affiliations', musts=['record'])
def affiliated_with(model, element):
    recid = get_recid_from_ref(element['record'])
    institution = make_node(InstitutionNode, recid=recid)
    add_outgoing_relation(model,
                          AFFILIATED_WITH, institution)
