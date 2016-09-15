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


def produce_labels_string(labels):
    return ''.join([':' + label for label in labels if label])


def produce_properties_string(properties):
    if properties:
        properties_strings = []
        for key, value in properties.items():
            value = str(value)
            properties_string = key + ':' + value
            properties_strings.append(properties_string)

        return '{{{}}}'.format(','.join(properties_strings))
    else:
        return ''

def produce_element_block(labels=None, properties=None, variable_name=''):
    if not labels: labels = []
    if not properties: properties = {}

    labels_string = produce_labels_string(labels)
    properties_string = produce_properties_string(properties)

    return '{node_variable}{labels_string}{properties_string}'.format(
        node_variable=variable_name, labels_string=labels_string,
        properties_string=properties_string
    )


def produce_node_block(labels=None, properties=None, variable_name=''):

    return '({})'.format(produce_element_block(labels, properties,
                                               variable_name))


def produce_relation_block(relation_type, properties=None, variable_name='',
                           arrow_left=False, arrow_right=False):

    if arrow_left and arrow_right:
        raise ValueError('Bidirectional relation not allowed in Cypher.')

    block = '-[{}]-'.format(
        produce_element_block([relation_type], properties, variable_name))

    if arrow_left:
        block = '<' + block
    if arrow_right:
        block += '>'

    return block


def delete_all():
    return (
        'MATCH () - [r] - () DELETE r;\n'
        'MATCH (n) DELETE n;\n'
    )


def create_node(labels=None, properties=None):

    if not labels: labels = []
    if not properties: properties = {}

    return 'CREATE ' + produce_node_block(labels, properties,
                                          variable_name='node')


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
                    end_node_labels=None, end_node_properties=None):
    """Creates relation between two nodes if they exist."""

    start_node = produce_node_block(start_node_labels, start_node_properties,
                                    variable_name='start_node')
    end_node = produce_node_block(end_node_labels, end_node_properties,
                                  variable_name='end_node')
    relation = produce_relation_block(relation_type, relation_properties,
                                      arrow_right=True)

    return 'MATCH {start_node}, {end_node} ' \
        'CREATE (start_node) {relation} (end_node)'.format(start_node=start_node,
                                                           end_node=end_node,
                                                           relation=relation)


# def create_record(recid, labels=None, properties=None):
#     if not labels: labels = []
#     if not properties: properties = {}
#
#     labels = ['Record'] + labels
#     properties['recid'] = recurl
#     return create_node(labels, properties)


# def delete_record(recurl):
#     """Deletes record and all relations attached"""
#     return delete_node(['Record'], {'recurl': recurl})


# def connect_records(relation_type, start_recurl, end_recurl,
#                     relation_properties=None):
#     return create_relation(relation_type, relation_properties,
#                            start_node_labels=['Record'],
#                            start_node_properties={'recurl': start_recurl},
#                            end_node_labels=['Record'],
#                            end_node_properties={'recurl': end_recurl})


# def connect_record_to_node(relation_type, recurl, node_labels=None,
#                            node_properties=None, relation_properties=None):
#     """"Creates relation between record and a given node if they exist.
#     If there is more than one node with given set of labels and properties,
#     more than one relation will be created."""
#
#     return create_relation(relation_type, relation_properties,
#                            start_node_labels=['Record'],
#                            start_node_properties={'recurl': recurl},
#                            end_node_labels=node_labels,
#                            end_node_properties=node_properties)


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


# def get_node(node_labels=None, node_properties=None, var_name='n'):
#     return 'MATCH {node} RETURN {var_name}'.format(
#         node=produce_node_block(labels=node_labels, properties=node_properties,
#                                 variable_name=var_name),
#         var_name=var_name
#     )
#
#
# def get_record(recurl, var_name='record'):
#     return get_node(node_labels=['Record'],
#                     node_properties={'recurl': recurl}, var_name=var_name)


def create_relations_from_csv(file_name, relation_type,
                              start_node_labels, end_node_labels):
    file_url = '\'file:///' + file_name + '\''
    relation_string = create_relation(relation_type,
                                      start_node_labels=start_node_labels,
                                      start_node_properties={
                                          'uid':'line.start_node_uid'},
                                      end_node_labels=end_node_labels,
                                      end_node_properties={
                                          'uid': 'line.end_node_uid'},
                                      )

    return (
        'USING PERIODIC COMMIT 10000\n'
        'LOAD CSV WITH HEADERS FROM '+ file_url + ' AS line\n\n'
        + relation_string + ';\n\n'
    )


def create_node_from_csv(file_name, labels, properties, add_uid=False):
    mapping = {key: 'line.' + value for key, value in properties.items()}
    if add_uid:
        mapping['uid'] = 'line.uid'

    file_url = '\'file:///' + file_name + '\''
    return (
        'USING PERIODIC COMMIT 10000\n'
        'LOAD CSV WITH HEADERS FROM '+ file_url + ' AS line\n\n'
        + create_node(labels=labels, properties=mapping) + ';\n\n'
        )


def create_index(label, property_name):

    return 'CREATE INDEX ON :{label}({property_name});\n'.format(
        label = label,
        property_name = property_name
    )
