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

from ..conferences.builder import conferences
from ..experiments import experiments
from ..hepnames.builder import hepnames
from ..institutions import institutions
from ..jobs import jobs
from ..journals import journals
from ..literature import literature

from inspirehep.modules.relations.graph_representation import make_node
from inspirehep.modules.relations.model_updaters import (
    add_label_to_central_node,
    add_outgoing_relation
    )

from inspirehep.modules.relations.model.nodes import (
    CountryNode,
    ResearchFieldNode
    )
from inspirehep.modules.relations.model.relations import (
    IN_THE_FIELD_OF,
    LOCATED_IN
    )


@institutions.element_processor('address', musts=['country_code'])
@conferences.element_processor('address', musts=['country_code'])
def located_in_country(model, element):
    country = make_node(CountryNode,
                              country_code=element['country_code'])
    add_outgoing_relation(model,
                          LOCATED_IN, country)


@conferences.element_processor('field_categories')
@jobs.element_processor('field_categories')
@literature.element_processor('field_categories')
def in_the_field_of(model, element):
    research_field = make_node(ResearchFieldNode,
                               field_name=element['term'])
    add_outgoing_relation(model,
                          IN_THE_FIELD_OF, research_field)
