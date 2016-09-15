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

from inspirehep.modules.relations.exceptions import MissingUid
from inspirehep.modules.relations.utils import extract_element
from frozendict import frozendict


class BaseNodeType(object):

    create_if_does_not_exist = False
    default_labels = set()

    @staticmethod
    def generate_uid(*args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def create_graph_dict_from_uid(cls, uid):
        raise NotImplementedError()


def create_graph_dict(central_node_type=BaseNodeType):
    graph_dict = {
        'node': make_node(central_node_type, force_uid=False),
        'outgoing_relations': set()
    }

    if central_node_type:
        central_node = get_central_node(graph_dict)
        add_node_labels(central_node,
                        *central_node_type.default_labels)

    return graph_dict


def render_graph_dict(graph_dict):
    central_node = graph_dict['node'] = freeze_node(
        graph_dict['node'])
    graph_dict['outgoing_relations'] = set(
        map(
            lambda rel: (central_node,) + rel,
            graph_dict['outgoing_relations']
        )
    )


def make_node(node_type=BaseNodeType, force_uid=True, **kwargs):
    uid = kwargs.get('uid')
    properties = kwargs.get('properties', {})
    labels = kwargs.get('labels', set())
    if force_uid and not uid:
        uid = node_type.generate_uid(**kwargs)
    return [node_type, uid, labels, properties]


def freeze_node(node):
    return node[0], node[1], frozenset(node[2]), frozendict(node[3])


class GraphModelBuilder:

    def __init__(self, central_node_type,
                 element_types=None, graph_updaters=None):
        self._central_node_type = central_node_type
        self._element_types = (element_types
                               if element_types is not None else {})
        self._graph_updaters = (graph_updaters
                                if graph_updaters is not None else {})

    def element_processor(self, field=None, musts=None):
        if not musts: musts = []
        def decorator(processor):
            self._graph_updaters[processor.func_name] = processor
            self._element_types[processor.func_name] = (field, musts)
            return processor
        return decorator


    @property
    def required_fields(self):
        return [
            element_def[0] for _, element_def in self._element_types.items()
            ]

    def update_graph_model(self, graph_model, element_type, element):
        self._graph_updaters[element_type](graph_model, element)

    def build(self, record):
        graph_dict = create_graph_dict(self._central_node_type)

        for element_type, element_definition in self._element_types.items():
            elements = extract_element(record, element_definition[0],
                                       element_definition[1])
            for element in elements:
                self.update_graph_model(graph_dict, element_type, element)

        uid = get_node_uid(
            get_central_node(graph_dict)
            )
        if not uid:
            raise MissingUid(
                'Graph updaters haven\'t set central node\'s UID')

        render_graph_dict(graph_dict)

        return graph_dict


def get_node_type(node):
    return node[0]


def set_node_type(node, node_type):
    node[0] = node_type


def get_node_uid(node):
    return node[1]


def set_node_uid(node, uid):
    node[1] = uid


def get_node_labels(node):
    return node[2]


def add_node_labels(node, *labels):
    node[2].update(set(labels))


def remove_node_labels(node, *labels):
    for label in labels:
        try:
            node[2].remove(label)
        except KeyError:
            pass


def get_node_properties(node):
    return node[3]


def add_node_properties(node, properties):
    node[3].update(properties)


def remove_node_properties(node, *keys):
    for key in keys:
        try:
            del node[3][key]
        except KeyError:
            pass


def get_outgoing_relations(model):
    return model['outgoing_relations']


def get_central_node(model):
    return model['node']


def get_relation_type(relation):
    return relation[1]


def get_relation_properties(relation):
    return relation[3]


def get_start_node(relation):
    return relation[0]


def get_end_node(relation):
    return relation[2]


def should_create_start_node_if_not_exists(relation):
    start_node = get_start_node(relation)
    return get_node_type(start_node).create_if_does_not_exist


def should_create_end_node_if_not_exists(relation):
    end_node = get_end_node(relation)
    return get_node_type(end_node).create_if_does_not_exist


def produce_model_from_node(node):
    node_type = get_node_type(node)
    try:
        model = node_type.create_graph_dict_from_uid(
            get_node_uid(node)
            )
    except NotImplementedError:
        raise TypeError('Node cannot produce model from uid.')
    return model
