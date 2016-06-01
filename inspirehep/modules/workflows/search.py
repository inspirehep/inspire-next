# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Search factory for INSPIRE workflows UI.

We specify in this custom search factory which fields elasticsearch should
return in order to not always return the entire record.

Add a key path to the includes variable to include it in the API output when
listing/searching across workflow objects (Holding Pen).
"""

from __future__ import absolute_import, division, print_function

from invenio_workflows_ui.search import default_search_factory


def holdingpen_search_factory(self, search, **kwargs):
    """Override search factory."""
    search, urlkwargs = default_search_factory(self, search, **kwargs)
    includes = [
        'metadata.titles', 'metadata.abstracts', 'metadata.subject_terms',
        'metadata.authors', 'metadata.name',
        '_workflow', '_extra_data.relevance_prediction',
        '_extra_data.user_action',
        '_extra_data.classifier_results.complete_output'
    ]
    search = search.extra(_source={"include": includes})
    return search, urlkwargs
