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

"""INSPIRE search factory used in invenio-records-rest."""

from __future__ import absolute_import, division, print_function

import json

from flask import current_app, request

from invenio_records_rest.errors import InvalidQueryRESTError
from invenio_records_rest.facets import _aggregations, _query_filter, \
    _post_filter
from invenio_records_rest.sorter import default_sorter_factory
from werkzeug.datastructures import MultiDict

from inspirehep.modules.search import LiteratureSearch
from inspirehep.modules.search.utils import get_facet_configuration


def select_source(search):
    """If search_idex is records-hep it filters the output to get only
    the useful data.

    Args:
        search: Elastic search DSL search instance.
        search_index: Index name

    Returns: Elastic search DSL search instance.
    """
    if isinstance(search, LiteratureSearch):
        request_accept = request.headers.get('Accept')
        if request_accept == 'application/vnd+inspire.record.ui+json':
            #  If it's search from UI then use _ui_display field only
            search = search.source(
                includes=[
                    "$schema",
                    "control_number",
                    "_ui_display"
                ]
            )
        else:
            search = search.source(
                includes=[
                    "$schema",
                    "abstracts.value",
                    "arxiv_eprints.value",
                    "arxiv_eprints.categories",
                    "authors.affiliations",
                    "authors.full_name",
                    "authors.inspire_roles",
                    "authors.control_number",
                    "collaborations",
                    "control_number",
                    "citation_count",
                    "dois.value",
                    "earliest_date",
                    "inspire_categories",
                    "number_of_references",
                    "publication_info",
                    "report_numbers",
                    "titles.title"
                ]
            )
    return search


def default_inspire_facets_factory(search, index):
    urlkwargs = MultiDict()

    facets = get_facet_configuration(index)

    if facets:
        search = _aggregations(search, facets.get("aggs", {}))
        search, urlkwargs = _query_filter(
            search, urlkwargs, facets.get("filters", {}))
        search, urlkwargs = _post_filter(
            search, urlkwargs, facets.get("post_filters", {}))

    return search, urlkwargs


def inspire_filter_factory(search, urlkwargs, search_index):
    """Copies behaviour of default facets factory but without the aggregations,
    As facets factory is also responsible for filtering the year and author (invenio mess)
    Args:
        search: Elastic search DSL search instance.
        urlkwargs:
        search_index: index name

    Returns: tuple with search and urlarguments

    """
    facets = get_facet_configuration(search_index)
    # Query filter
    search, urlkwargs = _query_filter(
        search, urlkwargs, facets.get("filters", {}))

    # Post filter
    search, urlkwargs = _post_filter(
        search, urlkwargs, facets.get("post_filters", {}))

    return search, urlkwargs


def inspire_search_factory(self, search):
    """Parse query using Inspire-Query-Parser.

    :param self: REST view.
    :param search: Elastic search DSL search instance.
    :returns: Tuple with search instance and URL arguments.
    """
    query_string = request.values.get('q', '')
    urlkwargs = MultiDict()

    try:
        search = search.query_from_iq(query_string)
    except SyntaxError:
        current_app.logger.debug(
            "Failed parsing query: {0}".format(
                request.values.get('q', '')),
            exc_info=True)
        raise InvalidQueryRESTError()

    search_index = search._index[0]
    search, urlkwargs = inspire_filter_factory(search, urlkwargs, search_index)
    search, sortkwargs = default_sorter_factory(search, search_index)
    search = select_source(search)

    urlkwargs.add('q', query_string)
    current_app.logger.debug(json.dumps(search.to_dict(), indent=4))

    return search, urlkwargs


def inspire_facets_factory(self, search):
    """Parse query using Inspire-Query-Parser and prepare facets for it
    Args:
        self: REST view.
        search: Elastic search DSL search instance.

    Returns: Tuple with search instance and URL arguments.

    """
    query_string = request.values.get('q', '')
    try:
        search = search.query_from_iq(query_string)
    except SyntaxError:
        current_app.logger.debug(
            "Failed parsing query: {0}".format(
                request.values.get('q', '')),
            exc_info=True)
        raise InvalidQueryRESTError()

    search_index = search._index[0]
    search, urlkwargs = default_inspire_facets_factory(search, search_index)
    search = select_source(search)

    urlkwargs.add('q', query_string)
    current_app.logger.debug(json.dumps(search.to_dict(), indent=4))

    return search, urlkwargs
