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

from frozendict import frozendict

from graph_representation import (
    add_node_labels,
    add_node_properties,
    freeze_node,
    get_central_node,
    remove_node_labels,
    remove_node_properties,
    set_node_uid
    )


def add_label_to_central_node(model, label):
    central_node = get_central_node(model)
    add_node_labels(central_node, label)


def remove_label_from_central_node(model, label):
    central_node = get_central_node(model)
    remove_node_labels(central_node, label)


def set_property_of_central_node(model, name, value):
    central_node = get_central_node(model)
    add_node_properties(central_node, {name: value})


def remove_property_from_central_node(model, name):
    central_node = get_central_node(model)
    remove_node_properties(central_node, name)


def set_uid(model, uid):
    central_node = get_central_node(model)
    set_node_uid(central_node, uid)


def add_outgoing_relation(model, relation_type, end_node, properties=None):
    if properties is None: properties = {}
    model['outgoing_relations'].add(
        (relation_type, freeze_node(end_node),
         frozendict(properties))
    )
