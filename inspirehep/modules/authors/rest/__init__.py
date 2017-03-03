# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Record serialization."""

from __future__ import absolute_import, division, print_function

from inspirehep.modules.authors.rest.citations import AuthorAPICitations
from inspirehep.modules.authors.rest.coauthors import AuthorAPICoauthors
from inspirehep.modules.authors.rest.publications import AuthorAPIPublications
from inspirehep.modules.authors.rest.stats import AuthorAPIStats
from inspirehep.modules.records.serializers.response import (
    record_responsify_nocache,
)

citations_v1 = AuthorAPICitations()
citations_v1_response = record_responsify_nocache(citations_v1,
                                                  'application/json')

coauthors_v1 = AuthorAPICoauthors()
coauthors_v1_response = record_responsify_nocache(coauthors_v1,
                                                  'application/json')

publications_v1 = AuthorAPIPublications()
publications_v1_response = record_responsify_nocache(publications_v1,
                                                     'application/json')

stats_v1 = AuthorAPIStats()
stats_v1_response = record_responsify_nocache(stats_v1,
                                              'application/json')
