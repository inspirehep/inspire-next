/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014, 2015, 2016 CERN.
 *
 * INSPIRE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

require.config({
  baseUrl: '/static/',
  paths: {
    'angular': 'node_modules/angular/angular',
    'angular-filter': 'node_modules/angular-filter/dist/angular-filter',
    'angular-hotkeys': 'node_modules/angular-hotkeys-light/angular-hotkeys-light',
    'angular-loading-bar': 'node_modules/angular-loading-bar/build/loading-bar',
    'angular-sanitize': 'node_modules/angular-sanitize/angular-sanitize',
    'angular-ui-bootstrap': 'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-tpls',
    'angular-xeditable': 'node_modules/angular-xeditable/dist/js/xeditable',
    'author': 'js/authors/author',
    'bootstrap': 'node_modules/bootstrap-sass/assets/javascripts/bootstrap',
    'bootstrap-datetimepicker': 'node_modules/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker',
    'bootstrap-multiselect': 'node_modules/bootstrap-multiselect/dist/js/bootstrap-multiselect',
    'bucketsjs': 'node_modules/buckets-js/dist/buckets',
    'clipboard': 'node_modules/clipboard/dist/clipboard',
    'd3': 'node_modules/d3/d3',
    'd3-tip': 'node_modules/d3-tip/index',
    'd3wrapper': 'js/d3-wrapper',
    'datatables': 'node_modules/datatables.net-bs/js/dataTables.bootstrap',
    'datatables.net': 'node_modules/datatables.net/js/jquery.dataTables',
    'default_typeahead_configuration': 'node_modules/inspirehep-typeahead-search-js/src/default_typeahead_configuration',
    'feedback': 'js/feedback/feedback',
    'flight': 'node_modules/flightjs/build/flight',
    'hgn': 'node_modules/requirejs-hogan-plugin/hgn',
    'hogan': 'node_modules/hogan.js/web/builds/3.0.2/hogan-3.0.2.amd',
    'impact-graphs': 'node_modules/impact-graphs/impact-graph',
    'inspirehep-clipboard': 'js/inspire_clipboard',
    'inspirehep-search': 'node_modules/inspirehep-search-js/dist/inspirehep-search',
    'inspirehep-typeahead': 'node_modules/inspirehep-typeahead-search-js/src/typeahead',
    'invenio-search': 'node_modules/invenio-search-js/dist/invenio-search-js',
    'invenio_with_spires_typeahead_configuration': 'node_modules/inspirehep-typeahead-search-js/src/invenio_with_spires_typeahead_configuration',
    'jquery': 'node_modules/jquery/jquery',
    'jquery-caret': 'node_modules/jquery-plugin/dist/jquery.caret-1.5.0',
    'jquery.ui': 'node_modules/jquery-ui/jquery-ui',
    'microplugin': 'node_modules/microplugin/src/microplugin',
    'moment': 'node_modules/moment/moment',
    'ngclipboard': 'node_modules/ngclipboard/src/ngclipboard',
    'profile': 'js/authors/profile',
    'publications': 'js/authors/publications',
    'readmore': 'node_modules/readmore-js/readmore',
    'search_parser': 'node_modules/inspirehep-typeahead-search-js/src/search_parser',
    'sifter': 'node_modules/sifter/sifter',
    'statistics': 'js/authors/statistics',
    'text': 'node_modules/requirejs-hogan-plugin/text',
    'typeahead': 'node_modules/typeahead.js/dist/typeahead.bundle',
  },
  shim: {
    'angular': {
      exports: 'angular',
    },
    'angular-filter': {
      deps: [
        'angular',
      ],
    },
    'angular-hotkeys': {
      deps: [
        'angular',
      ],
    },
    'angular-loading-bar': {
      deps: [
        'angular',
      ],
    },
    'angular-sanitize': {
      deps: [
        'angular',
      ],
    },
    'angular-ui-bootstrap': {
      deps: [
        'angular',
      ],
    },
    'angular-xeditable': {
      deps: [
        'angular',
        'jquery',
      ],
    },
    'bootstrap': {
      deps: [
        'jquery',
        'jquery.ui',
      ],
    },
    'bootstrap-datetimepicker': {
      deps: [
        'bootstrap',
        'jquery',
        'moment',
      ],
      exports: '$.fn.datetimepicker',
    },
    'bootstrap-multiselect': {
      deps: [
        'jquery',
      ],
      exports: '$.fn.multiselect',
    },
    'impact-graphs': {
      deps: [
        'd3wrapper',
      ],
      exports: 'ImpactGraph',
    },
    'inspirehep-search': {
      deps: [
        'angular',
        'angular-filter',
        'angular-loading-bar',
        'invenio-search',
        'angular-ui-bootstrap',
        'angular-xeditable',
        'angular-hotkeys',
        'angular-sanitize',
        'ngclipboard'
      ],
    },
    'invenio-search': {
      deps: [
        'angular',
      ],
    },
    'jquery': {
      exports: '$',
    },
    'jquery-caret': {
      deps: [
        'jquery',
      ],
      exports: '$.fn.caret',
    },
    'jquery.ui': {
      deps: [
        'jquery',
      ],
    },
    'ngclipboard': {
      deps: [
        'angular',
        'clipboard',
        'inspirehep-clipboard',
      ],
    },
    'typeahead': {
      deps: [
        'jquery',
      ],
      exports: 'Bloodhound',
    },
  },
});
