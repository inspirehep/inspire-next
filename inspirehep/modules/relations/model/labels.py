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

class NodeLabels:

    Record = 'Record'
    Experiment = 'Experiment'
    Conference = 'Conference'
    Person = 'Person'
    Institution = 'Institution'
    Job = 'Job'
    Journal = 'Journal'
    Literature = 'Literature'

    Published = 'Published'
    arXiv = 'ArXiv'
    ConferencePaper = 'ConferencePaper'
    Thesis = 'Thesis'
    Review = 'Review'
    Lectures = 'Lectures'
    Note = 'Note'
    Proceedings = 'Proceedings'
    Introductory = 'Introductory'
    Book = 'Book'
    BookChapter = 'BookChapter'
    Report = 'Report'

    Country = 'Country'
    Continent = 'Continent'
    ScientificRank = 'ScientificRank'
    ResearchField = 'ResearchField'
    ConferenceSeries = 'ConferenceSeries'
    Publisher = 'Publisher'
    Author = 'Author'
    Degree = 'Degree'
    CurrentJobPosition = 'CurrentJobPosition'
    PreviousJobPosition = 'PreviousJobPosition'


class RelationLabels:

    AFFILIATED_WITH = 'AFFILIATED_WITH'
    AUTHORED_BY = 'AUTHORED_BY'
    AT = 'AT'
    CONTRIBUTED_TO = 'CONTRIBUTED_TO'
    HIRED_AS = 'HIRED_AS'
    IN_THE_FIELD_OF = 'IN_THE_FIELD_OF'
    IN_THE_RANK_OF = 'IN_THE_RANK_OF'
    IS_ABOUT_EXPERIMENT = 'IS_ABOUT_EXPERIMENT'
    LOCATED_IN = 'LOCATED_IN'
    OFFERED_BY = 'OFFERED_BY'
    PUBLISHED_BY = 'PUBLISHED_BY'
    REFERS_TO = 'REFERS_TO'
    REPRESENTS = 'REPRESENTS'
    SUPERVISED_BY = 'SUPERVISED_BY'
    WRITTEN_BY = 'WRITTEN_BY'
