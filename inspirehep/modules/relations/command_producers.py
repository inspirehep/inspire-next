# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from inspirehep.modules.relations.model.nodes import RecordNode

def produce_labels_string(labels):
    return ''.join([':' + label for label in labels if label])


def produce_properties_string(properties, add_quotes=True):
    if properties:
        properties_strings = []
        for key, value in properties.items():
            value = str(value)
            if add_quotes and isinstance(value, str):
                value = "'" + str(value) + "'"
            properties_string = key + ':' + value
            properties_strings.append(properties_string)

        return '{{{}}}'.format(','.join(properties_strings))
    else:
        return ''


def produce_element_block(labels=None, properties=None, variable_name='',
                          add_quotes_to_properties=True):
    if not labels: labels = []
    if not properties: properties = {}

    labels_string = produce_labels_string(labels)
    properties_string = produce_properties_string(
        properties, add_quotes=add_quotes_to_properties)

    return '{node_variable}{labels_string}{properties_string}'.format(
        node_variable=variable_name, labels_string=labels_string,
        properties_string=properties_string
    )


def produce_node_block(labels=None, properties=None, variable_name='',
                       add_quotes_to_properties=True):

    return '({})'.format(produce_element_block(
        labels, properties, variable_name,
        add_quotes_to_properties=add_quotes_to_properties))


def produce_relation_block(relation_type, properties=None, variable_name='',
                           arrow_left=False, arrow_right=False,
                            add_quotes_to_properties=True):

    if arrow_left and arrow_right:
        raise ValueError('Bidirectional relation not allowed in Cypher.')

    block = '-[{}]-'.format(
        produce_element_block(
            [relation_type], properties, variable_name,
            add_quotes_to_properties=add_quotes_to_properties))

    if arrow_left:
        block = '<' + block
    if arrow_right:
        block += '>'

    return block


def delete_all():
    return 'MATCH (a) DETACH DELETE a;\n'


def create_node(labels=None, properties=None, add_quotes_to_properties=True):

    if not labels: labels = []
    if not properties: properties = {}

    return 'CREATE ' + produce_node_block(
        labels, properties, variable_name='node',
        add_quotes_to_properties=add_quotes_to_properties)


def delete_node(labels=None, properties=None):

    if not labels: labels = []
    if not properties: properties = {}

    """Deletes node with given labels and properties
    and all relations_attached to it"""
    node = produce_node_block(labels, properties, variable_name='node')
    return "MATCH {node} OPTIONAL MATCH node - [relation] - () " \
        "DELETE node, relation".format(node=node)


def create_relation(relation_type, relation_properties=None,
                    start_node_labels=None, start_node_properties=None,
                    end_node_labels=None, end_node_properties=None,
                    add_quotes_to_properties=True):
    """Creates relation between two nodes if they exist."""

    start_node = produce_node_block(
        start_node_labels, start_node_properties, variable_name='start_node',
        add_quotes_to_properties=add_quotes_to_properties)
    end_node = produce_node_block(
        end_node_labels, end_node_properties, variable_name='end_node',
        add_quotes_to_properties=add_quotes_to_properties)
    relation = produce_relation_block(
        relation_type, relation_properties, arrow_right=True,
        add_quotes_to_properties=add_quotes_to_properties)

    return 'MATCH {start_node}, {end_node} ' \
        'CREATE (start_node) {relation} (end_node)'.format(
            start_node=start_node, end_node=end_node, relation=relation)


def get_outgoing_relations(node_labels, node_properties, relation_type=None,
                           relation_properties=None, var_name='r'):
    return 'MATCH {node} {relation} () RETURN {var}'.format(
        node=produce_node_block(
            labels=node_labels, properties=node_properties),
        relation=produce_relation_block(relation_type=relation_type,
                                        properties=relation_properties,
                                        arrow_right=True, variable_name=var_name),
        var=var_name
    )


def get_all_outgoing_relations(node_labels, node_properties, var_name):
    return get_outgoing_relations(node_labels=node_labels,
                                  node_properties=node_properties,
                                  var_name=var_name)


def make_file_url(file_path):
    return '\'file:///' + file_path + '\''


def create_relations_from_csv(file_name, relation_type,
                              start_node_labels, end_node_labels,
                              relation_properties):
    relations_mapping = {
        property: 'line.' + property for property in relation_properties}
    file_url = make_file_url(file_name)

    relation_string = create_relation(
        relation_type, relation_properties=relations_mapping,
        start_node_labels=start_node_labels,
        start_node_properties={'uid':'line.start_node_uid'},
        end_node_labels=end_node_labels,
        end_node_properties={'uid': 'line.end_node_uid'},
        add_quotes_to_properties=False
        )

    return (
        'USING PERIODIC COMMIT 10000\n'
        'LOAD CSV WITH HEADERS FROM '+ file_url + ' AS line\n\n'
        + relation_string + ';\n\n'
    )


def create_node_from_csv(file_name, labels, properties_set, add_uid=False):
    mapping = {property: 'line.' + property for property in properties_set}
    if add_uid:
        mapping['uid'] = 'line.uid'

    file_url = make_file_url(file_name)
    return (
        'USING PERIODIC COMMIT 10000\n'
        'LOAD CSV WITH HEADERS FROM '+ file_url + ' AS line\n\n'
        + create_node(labels=labels, properties=mapping,
                      add_quotes_to_properties=False) + ';\n\n'
        )


def create_index(label, property_name):

    return 'CREATE INDEX ON :{label}({property_name});\n'.format(
        label = label,
        property_name = property_name
    )


def match_node(node_type, variable_name='', **kwargs):
    uid = node_type.generate_uid(**kwargs)
    node = produce_node_block(labels=node_type.default_labels,
                              properties={'uid': uid},
                              variable_name=variable_name)
    return 'MATCH {} '.format(node)


def match_record(recid, variable_name):
    return match_node(RecordNode, variable_name=variable_name, recid=recid)


def render_query(blocks):
    return ' '.join(blocks) + '; '
