# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from inspirehep.modules.relations.model.nodes import RecordNode
from inspirehep.modules.relations.command_producers import (
    produce_node_block,
    produce_relation_block
)


def match_record(recid, variable_name=''):
    uid = RecordNode.generate_uid(recid)
    return 'MATCH {}'.format(
        produce_node_block(labels=RecordNode.default_labels,
                           properties={'uid': "'" + uid + "'"},
                           variable_name=variable_name)
    )


def render_query(blocks):
    return ' '.join(blocks) + '; '


# def match_records_ingoing_relations(recid, relation_type=None,
#                                     relation_properties=None
#                                     relation_variable='',
#                                     record_variable='',
#                                     start_node_variable=''):
#     uid = RecordNode.generate_uid(recid)
#     record_block = produce_node_block(labels=RecordNode.default_labels,
#                                          properties={'uid': uid},
#                                          variable_name=record_variable)
#     relation = produce_relation_block(relation_type,
#                                       properties=relation_properties
#                                       )
#     return 'MATCH ' +
