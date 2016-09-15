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


import click
import csv

from functools import partial

import os

import shutil
import subprocess
from uuid import uuid4

from inspirehep.modules.relations import current_db_session

import inspirehep.modules.relations.command_producers as commands
from inspirehep.modules.relations.model.indices import (
    INDICES_TO_CREATE
)
from inspirehep.modules.relations import builders
from inspirehep.modules.relations.graph_representation import (
    get_central_node,
    get_node_labels,
    get_node_properties,
    get_node_uid,
    get_node_type,
    get_outgoing_relations,
    get_relation_type,
    get_start_node,
    get_end_node,
    produce_model_from_node,
    should_create_end_node_if_not_exists
)
from inspirehep.modules.relations.model.pregenerate import pregenerate_graph
from inspirehep.modules.pidstore.providers import InspireRecordIdProvider

INDEX_TO_BUILDER = {
    'authors': builders.hepnames.hepnames,
    'journals': builders.journals.journals,
    'jobs': builders.jobs.jobs,
    'literature': builders.literature.literature,
    'experiments': builders.experiments.experiments,
    'conferences': builders.conferences.conferences,
    'institutions': builders.institutions.institutions
}

NODES_SUBDIRECTORY = 'nodes'
RELATIONS_SUBDIRECTORY = 'relations'

def nested_setdefault(dictionary, keys, default=None):
    current_dict = dictionary
    for key in keys[:-1]:
        try:
            current_dict = current_dict.setdefault(key, dict())
        except AttributeError:
            raise TypeError(
                'Wrong internal structure. ' + '.'.join(
                    keys[:keys.index(key)]
                    ) + ' is already something else than dict.'
                )
    return current_dict.setdefault(keys[-1], default)


def make_labels_key(labels):
    return tuple(sorted(labels))


def make_properties_key(properties):
    return tuple(sorted(properties.keys()))


def move_central_node_to_proper_group(node, groups):
    labels_key = make_labels_key(get_node_labels(node))
    properties_key = make_properties_key(get_node_properties(node))

    nested_setdefault(groups,
                      [labels_key, properties_key],
                      list()).append(node)


def move_relation_to_proper_group(relation, groups):
    relation_type = get_relation_type(relation)
    start_node_type = get_node_type(get_start_node(relation))
    end_node_type = get_node_type(get_end_node(relation))

    nested_setdefault(groups,
                      [relation_type, start_node_type, end_node_type],
                      list()).append(relation)


def process_record_model(model,
                         existing_uids, nodes_to_create, relations_to_create):
    central_node = get_central_node(model)
    central_uid = get_node_uid(central_node)

    if central_uid not in existing_uids:
        existing_uids.add(central_uid)
        move_central_node_to_proper_group(central_node,
                                          nodes_to_create)

        outgoing_relations = get_outgoing_relations(model)

        for relation in outgoing_relations:
            move_relation_to_proper_group(relation,
                                          relations_to_create)

            if should_create_end_node_if_not_exists(relation):
                end_node_model = produce_model_from_node(
                    get_end_node(relation))
                process_record_model(end_node_model,
                                     existing_uids,
                                     nodes_to_create,
                                     relations_to_create)


def generate_file_name():
    return str(uuid4()) + '.csv'


def generate_csv_for_nodes(nodes_to_create, directory):
    loader_file_name = os.path.join(directory, 'loader.cypher')

    with open(loader_file_name, 'w') as loader_file:
        for labels_set, nodes_subset in nodes_to_create.items():
            for properties_set, nodes in nodes_subset.items():

                node_properties = list(properties_set)
                csv_file = os.path.join(directory,
                                        generate_file_name())

                nodes_to_csv(csv_file,
                             nodes,
                             labels_set,
                             node_properties,
                             add_uid=True)

                load_command = commands.create_node_from_csv(
                    csv_file,
                    labels_set,
                    {prop:prop for prop in node_properties},
                    add_uid=True
                    )

                loader_file.write(load_command)

    return loader_file_name


def traverse_relations_tree(relations_to_create):
    for r_type, rs_of_rel_type in relations_to_create.items():
        for start_n_type, rs_with_start_n_type in rs_of_rel_type.items():
            for end_n_type, rs_with_end_n_type in rs_with_start_n_type.items():
                yield start_n_type, r_type, end_n_type, rs_with_end_n_type


def generate_csv_for_relations(relations_to_create, directory,
                               existing_uids):
    loader_file_name = os.path.join(directory, 'loader.cypher')
    both_edge_nodes_exist = partial(start_and_end_node_exist,
                                    existing_uids=existing_uids)

    with open(loader_file_name, 'w') as loader_file:
        for start_node_type, relation_type, end_node_type, relations \
        in traverse_relations_tree(relations_to_create):
            csv_file = os.path.join(directory, generate_file_name())
            relations_to_csv(csv_file,
                             filter(both_edge_nodes_exist, relations),
                             relation_type,
                             start_node_type,
                             end_node_type)

            load_command = commands.create_relations_from_csv(
                csv_file,
                relation_type,
                start_node_type.default_labels,
                end_node_type.default_labels
                )

            loader_file.write(load_command)

    return loader_file_name

def start_and_end_node_exist(relation, existing_uids):
    start_node_uid = get_node_uid(get_start_node(relation))
    end_node_uid = get_node_uid(get_end_node(relation))

    return start_node_uid in existing_uids and end_node_uid in existing_uids


def relations_to_csv(file_name, relations, relation_type,
                     start_node_labels, end_node_labels):
    with open(file_name, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(
            ['start_node_uid', 'end_node_uid']
        )

        for relation in relations:
            start_uid = get_node_uid(get_start_node(relation))
            end_uid = get_node_uid(get_end_node(relation))

            csv_writer.writerow([start_uid, end_uid])


def nodes_to_csv(file_name, nodes, labels, properties,
                 add_uid=False):
    with open(file_name, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        properties_header = properties
        if add_uid:
            properties_header = ['uid'] + properties_header
        csv_writer.writerow(properties_header)

        for node in nodes:
            node_properties = get_node_properties(node)
            node_data = map(
                lambda p: node_properties.get(p),
                properties
                )
            if add_uid:
                node_data = [get_node_uid(node)] + node_data

            try:
                csv_writer.writerow(node_data)
            except UnicodeEncodeError:
                encoded_data = map(
                    lambda x: x.encode('utf-8') if isinstance(x,
                                                              unicode)
                    else x, node_data)
                csv_writer.writerow(encoded_data)


def prepare_directories(*args):
    for directory in args:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)


def generete_csv_files(nodes, relations, existing_uids, directory):
    nodes_directory = os.path.join(directory, NODES_SUBDIRECTORY)
    relations_directory = os.path.join(directory, RELATIONS_SUBDIRECTORY)

    prepare_directories(nodes_directory, relations_directory)

    click.echo("Generating CSV files for nodes")
    nodes_loader_file = generate_csv_for_nodes(nodes, nodes_directory)

    click.echo("Generating CSV files for relations")
    relations_loader_file = generate_csv_for_relations(relations,
                                                       relations_directory,
                                                       existing_uids)
    return nodes_loader_file, relations_loader_file


def generate_init_loader(indices_to_create, directory):
    loader_path = os.path.join(directory, 'init.cypher')
    with open(loader_path, 'w') as loader:
        loader.write(commands.delete_all())
        generate_indices(indices_to_create, loader)

    return loader_path


def generate_indices(indices, loader_file):
    for index in indices:
        command = commands.create_index(index['label'], index['property'])
        loader_file.write(command)


def records_to_models(records):
    for record_object in records:
        record = record_object.json
        index = InspireRecordIdProvider.schema_to_pid_type(record['$schema'])
        builder = INDEX_TO_BUILDER[index]

        yield builder.build(record)


def run_cypher_loaders(*args):
    for loader in args:
        command = "neo4j-shell -c < " + loader
        subprocess.Popen(command, shell=True).wait()


def run_loading_scripts(directory):
    init_load = os.path.join(directory, 'init.cypher')
    nodes_load = os.path.join(directory, NODES_SUBDIRECTORY,
                              'loader.cypher')
    relations_load = os.path.join(directory, RELATIONS_SUBDIRECTORY,
                                  'loader.cypher')

    # click.echo("Running CYPHER scripts")
    # run_cypher_loaders(init_load, nodes_load, relations_load)
    init_commands = get_commands_from_the_script(init_load)
    nodes_commands = get_commands_from_the_script(nodes_load)
    relations_commands = get_commands_from_the_script(relations_load)

    click.echo("Running CYPHER commands")
    click.echo("Init commands")
    run_cypher_commands(init_commands)
    click.echo("Nodes commands")
    run_cypher_commands(nodes_commands)
    click.echo("Relations commands")
    run_cypher_commands(relations_commands)


def get_commands_from_the_script(script_file):
    commands = []
    with open(script_file, 'r') as script:
        commands = map(lambda command: command.replace('\n', ' ').strip() + ';',
                      ''.join([line for line in script]).split(';'))
    return commands[:-1]


def run_cypher_commands(commands):
    for command in commands:
        print command
        _ = current_db_session.run(command)
        for info in _:
            print info


def generate_csv_and_cypher_scripts(records, records_count, csv_storage):
    prepare_directories(csv_storage)
    init_loader = generate_init_loader(INDICES_TO_CREATE, csv_storage)

    existing_uids = set()
    nodes_to_create = {}
    relations_to_create = {}

    click.echo("\nBuilding basic graph elements (countries etc.)")
    for model in pregenerate_graph():
        process_record_model(model, existing_uids, nodes_to_create,
                             relations_to_create)

    click.echo("Building records graph models")
    with click.progressbar(records_to_models(records),
                           length=records_count) as models:
        for model in models:
            process_record_model(model, existing_uids, nodes_to_create,
                                 relations_to_create)

    generete_csv_files(nodes_to_create, relations_to_create,
                       existing_uids, csv_storage)


def migrate(records, records_count, csv_storage):
    click.echo('\nMigration started.')
    generate_csv_and_cypher_scripts(records, records_count, csv_storage)
    run_loading_scripts(csv_storage)
    click.echo('Migration completed\n')
