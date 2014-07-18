# -*- coding: utf-8 -*-
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.
"""Inspire bundles."""
from invenio.ext.assets import Bundle

search = Bundle('js/search/invenio_with_spires_typeahead_configuration.js',
                'js/search/search_parser.js',
                'js/search/typeahead.js',
                'js/search/default_typeahead_configuration.js',
                'js/search/facet.js',
                output="search.js",
                filters="uglifyjs",
                weight=50)

search_css = Bundle('css/typeahead.js-bootstrap.css',
                    'css/search/search.css',
                    'css/search/searchbar.css',
                    output="search.css",
                    filters="cleancss",
                    weight=50)

formatter_css = Bundle('css/formatter/templates_detailed_inspire.css',
                       output="inspire-formatter.css",
                       filters="cleancss",
                       weight=0)
