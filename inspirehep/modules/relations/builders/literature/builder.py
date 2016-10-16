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

from itertools import chain

from inspirehep.dojson.utils import get_recid_from_ref
from inspirehep.utils.date import create_earliest_date
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import (get_title, get_value)

from inspirehep.modules.relations.graph_representation import (
    make_node,
    GraphModelBuilder
    )
from inspirehep.modules.relations.model.nodes import (
    AuthorNode,
    ConferenceNode,
    JournalNode,
    LiteratureNode,
    PersonNode
    )
from inspirehep.modules.relations.model.relations import (
    AUTHORED_BY,
    CONTRIBUTED_TO,
    PART_OF,
    PUBLISHED_IN,
    REFERS_TO,
    WRITTEN_BY
    )
from inspirehep.modules.relations.model.utils import COLLECTION_TO_LABEL

from inspirehep.modules.relations.model_updaters import (
    add_label_to_central_node,
    set_property_of_central_node,
    add_outgoing_relation,
    set_property_of_central_node,
    set_uid
)
from inspirehep.modules.relations.utils import (
    clear_string,
    pick_one_field_category
    )


literature = GraphModelBuilder(central_node_type=LiteratureNode)


@literature.element_processor('control_number')
def recid(model, element):
    set_property_of_central_node(model,
                                 'recid', str(element))

    set_uid(model,
            uid=LiteratureNode.generate_uid(recid=element))


@literature.element_processor('collections')
def paper_type(model, element):
    if 'primary' in element:
        label = COLLECTION_TO_LABEL.get(element['primary'].upper())
        if label:
            add_label_to_central_node(model, label)


@literature.element_processor('references', musts=["record"])
def refers_to(model, element):
    recid = get_recid_from_ref(element['record'])
    refered_paper = make_node(LiteratureNode, recid=recid)
    add_outgoing_relation(model,
                          REFERS_TO, refered_paper)


@literature.element_processor('publication_info')
def contributed_to(model, element):
    conference_data = element.get('conference_record')
    journal_data = element.get('journal_record')
    parent_data = element.get('parent_record')

    if conference_data:
        conference_recid = get_recid_from_ref(conference_data)
        conference = make_node(ConferenceNode,
                               recid=conference_recid)
        add_outgoing_relation(model,
                              CONTRIBUTED_TO, conference)
    if journal_data:
        journal_recid = get_recid_from_ref(journal_data)
        journal = make_node(JournalNode,
                            recid=journal_recid)

        add_outgoing_relation(model,
                              PUBLISHED_IN, journal)


    if parent_data:
        parent_recid = get_recid_from_ref(parent_data)
        parent_publication = make_node(LiteratureNode,
                                 recid=parent_recid)
        add_outgoing_relation(model,
                              PART_OF, parent_publication)


@literature.element_processor('authors', musts=['record'])
def authored_by(model, element):
    person_recid = get_recid_from_ref(element['record'])
    affiliations_recids = [get_recid_from_ref(aff.get('record'))
                           for aff in element.get('affiliations', [])
                           if aff.get('record')
                           ]
    author = make_node(AuthorNode, person_recid=person_recid,
                             affiliations=affiliations_recids)
    add_outgoing_relation(model,
                          AUTHORED_BY, author)

    person = make_node(PersonNode, recid=person_recid)
    add_outgoing_relation(model,
                          WRITTEN_BY, person)


@literature.element_processor()
def title(model, element):
    title = clear_string(get_title(element))
    set_property_of_central_node(model, 'title', title)


@literature.element_processor()
def display_research_field(model, element):
    """
    One of paper's research field chosen to display in citation summary
    """
    categories = [category['term'] for category in element.get(
        'field_categories', []) if 'term' in category]
    if categories:
        set_property_of_central_node(model, '_display_research_field',
                                     pick_one_field_category(categories))


@literature.element_processor()
def earliest_date(model, element):
    #TODO: this is copy-pasted from inspirehep/dojson/hep/receivers.py,
    # should be abstracted there and only imported here

    date_paths = [
        'preprint_date',
        'thesis.date',
        'thesis.defense_date',
        'publication_info.year',
        'creation_modification_date.creation_date',
        'imprints.date',
    ]

    dates = list(chain.from_iterable(
        [force_force_list(get_value(element, path)) for path in date_paths]))

    earliest_date = create_earliest_date(dates)
    if earliest_date:
        set_property_of_central_node(model, 'earliest_date', earliest_date)
