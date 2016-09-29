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

from __future__ import absolute_import, print_function

from inspirehep.modules.relations.graph_representation import GraphModelType

from inspirehep.modules.relations.model import nodes

class ConferenceGraphModel(GraphModelType):
    central_node_type = nodes.ConferenceNode

class ExperimentGraphModel(GraphModelType):
    central_node_type = nodes.ExperimentNode

class InstitutionGraphModel(GraphModelType):
    central_node_type = nodes.InstitutionNode

class JobGraphModel(GraphModelType):
    central_node_type = nodes.JobNode

class JournalGraphModel(GraphModelType):
    central_node_type = nodes.JournalNode

class LiteratureGraphModel(GraphModelType):
    central_node_type = nodes.LiteratureNode

class PersonGraphModel(GraphModelType):
    central_node_type = nodes.PersonNode
