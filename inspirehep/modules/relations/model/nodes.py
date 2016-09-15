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
    BaseNodeType,
    create_graph_dict,
    make_node,
    render_graph_dict
    )
from inspirehep.modules.relations.model.labels import NodeLabels
from inspirehep.modules.relations.model.relations import (
    AFFILIATED_WITH,
    AT,
    IN_THE_RANK_OF,
    REPRESENTS
    )

from inspirehep.modules.relations.model_updaters import (
    add_outgoing_relation,
    set_uid
    )

UID_BASIC_SEPARATOR = '|^|'
UID_SECONDARY_SEPARATOR = '|/|'


class RecordNode(BaseNodeType):

    default_labels = set([NodeLabels.Record])

    @staticmethod
    def generate_uid(recid):
        return UID_BASIC_SEPARATOR.join(['Record', str(recid)])


class AuthorNode(BaseNodeType):

    default_labels = set([NodeLabels.Author])
    create_if_does_not_exist = True

    @staticmethod
    def generate_uid(person_recid, affiliations=[]):
        sorted_affiliations = map(str, sorted(map(int, affiliations)))
        affiliations_string = UID_SECONDARY_SEPARATOR.join(sorted_affiliations)

        return UID_BASIC_SEPARATOR.join(
            ['Author', str(person_recid), affiliations_string]
            )

    @classmethod
    def create_graph_dict_from_uid(cls, uid):
        _, person_recid, affiliations_string = uid.split(UID_BASIC_SEPARATOR)
        affiliations_recids = affiliations_string.split(UID_SECONDARY_SEPARATOR)

        model = create_graph_dict(cls)
        set_uid(model, uid)

        person = make_node(PersonNode, recid=person_recid)
        add_outgoing_relation(model,
                              REPRESENTS, person)

        for affiliation_recid in affiliations_recids:
            institution = make_node(InstitutionNode, recid=affiliation_recid)
            add_outgoing_relation(model,
                                  AFFILIATED_WITH, institution)

        render_graph_dict(model)
        return model


class PreviousJobPositionNode(BaseNodeType):

    default_labels = set([NodeLabels.PreviousJobPosition])
    create_if_does_not_exist = True

    @staticmethod
    def generate_uid(rank_name, institution_recid, start_date, end_date):
        uid_elements = ['PreviousJobPosition'] + map(str,
                                                     [rank_name,
                                                      institution_recid,
                                                      start_date, end_date]
                                                     )

        return UID_BASIC_SEPARATOR.join(uid_elements)


    @classmethod
    def create_graph_dict_from_uid(cls, uid):
        _, rank_name, institution_recid, _, _ = uid.split(
            UID_BASIC_SEPARATOR
            )

        model = create_graph_dict(cls)
        set_uid(model, uid)

        rank = make_node(ScientificRankNode, rank_name=rank_name)
        institution = make_node(InstitutionNode, recid=institution_recid)

        add_outgoing_relation(model,
                              IN_THE_RANK_OF, rank)
        add_outgoing_relation(model,
                              AT, institution)

        render_graph_dict(model)

        return model


class CurrentJobPositionNode(BaseNodeType):

    default_labels = set([NodeLabels.CurrentJobPosition])
    create_if_does_not_exist = True

    @staticmethod
    def generate_uid(rank, institution_recid, start_date):
        uid_elements = ['CurrentJobPosition'] + map(str,
                                                     [rank, institution_recid,
                                                      start_date]
                                                     )
        return UID_BASIC_SEPARATOR.join(uid_elements)

    @classmethod
    def create_graph_dict_from_uid(cls, uid):

        _, rank_name, institution_recid, _ = uid.split(UID_BASIC_SEPARATOR)

        model = create_graph_dict(cls)
        set_uid(model, uid)

        rank =  make_node(ScientificRankNode, rank_name=rank_name)
        institution = make_node(InstitutionNode, recid=institution_recid)

        add_outgoing_relation(model,
                              IN_THE_RANK_OF, rank)
        add_outgoing_relation(model,
                              AT, institution)

        render_graph_dict(model)
        return model


class ConferenceNode(RecordNode):

    default_labels = RecordNode.default_labels | set(
        [NodeLabels.CurrentJobPosition])


class ContinentNode(BaseNodeType):

    default_labels = set([NodeLabels.Continent])

    @staticmethod
    def generate_uid(continent_name):
        return UID_BASIC_SEPARATOR.join(['Continent', continent_name])


class CountryNode(BaseNodeType):

    default_labels = set([NodeLabels.Country])

    @staticmethod
    def generate_uid(country_code):
        return UID_BASIC_SEPARATOR.join(['Country', country_code])


class ExperimentNode(RecordNode):

    default_labels = RecordNode.default_labels | set([NodeLabels.Experiment])


class InstitutionNode(RecordNode):

    default_labels = RecordNode.default_labels | set([NodeLabels.Institution])


class JournalNode(RecordNode):

    default_labels = RecordNode.default_labels | set([NodeLabels.Journal])


class JobNode(RecordNode):

    default_labels = RecordNode.default_labels | set([NodeLabels.Job])


class LiteratureNode(RecordNode):

    default_labels = RecordNode.default_labels | set([NodeLabels.Literature])


class PersonNode(RecordNode):

    default_labels = RecordNode.default_labels | set([NodeLabels.Person])


class PublisherNode(BaseNodeType):

    default_labels = set([NodeLabels.Publisher])

    @staticmethod
    def generate_uid(name):
        return UID_BASIC_SEPARATOR.join(['Publisher', name])


class ResearchFieldNode(BaseNodeType):

    default_labels = set([NodeLabels.ResearchField])

    @staticmethod
    def generate_uid(field_name):
        return UID_BASIC_SEPARATOR.join(['ResearchField', field_name])


class ScientificRankNode(BaseNodeType):

    default_labels = set([NodeLabels.ScientificRank])

    @staticmethod
    def generate_uid(rank_name):
        return UID_BASIC_SEPARATOR.join(['ScientificRank', rank_name])
