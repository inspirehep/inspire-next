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
    make_node,
    GraphModelBuilder
    )
from inspirehep.modules.relations.model.nodes import (
    CurrentJobPositionNode,
    PersonNode,
    PreviousJobPositionNode
    )
from inspirehep.modules.relations.model.relations import (
    HIRED_AS,
    SUPERVISED_BY
    )

from inspirehep.modules.relations.model_updaters import (
    add_outgoing_relation,
    set_property_of_central_node,
    set_uid
    )


hepnames = GraphModelBuilder(central_node_type=PersonNode)


@hepnames.element_processor('control_number')
def recid(model, element):
    set_property_of_central_node(model,
                                 'recid', str(element))

    set_uid(model,
            uid=PersonNode.generate_uid(recid=element))


@hepnames.element_processor('advisors', musts=['record'])
def gained_a_degree(model, element):
    supervisor_recid = get_recid_from_ref(element['record'])
    supervisor = make_node(PersonNode, recid=supervisor_recid)

    degree_type = element.get('degree_type')
    rel_properties = {'degree_type': degree_type} if degree_type else {}

    add_outgoing_relation(model,
                          SUPERVISED_BY, supervisor, rel_properties)


@hepnames.element_processor('positions', musts=['institution'])
def hired_as(model, element):
    institution_data = element['institution']

    if 'record' in institution_data:
        institution_recid = get_recid_from_ref(institution_data['record'])
        rank_name = element.get('rank')
        start_date = element.get('start_date')

        if element.get('current', ''):
            job_position = make_node(CurrentJobPositionNode,
                                     rank_name=rank_name,
                                     institution_recid=institution_recid,
                                     start_date=start_date
                                     )
        else:
            end_date = element.get('end_date')
            job_position = make_node(PreviousJobPositionNode,
                                     rank_name=rank_name,
                                     institution_recid=institution_recid,
                                     start_date=start_date,
                                     end_date=end_date
                                     )

        add_outgoing_relation(model,
                              HIRED_AS, job_position)
