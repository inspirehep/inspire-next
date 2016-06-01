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
    angular: 'node_modules/angular/angular',
    'angular-loading-bar': 'node_modules/angular-loading-bar/build/loading-bar',
    'angular-xeditable': 'node_modules/angular-xeditable/dist/js/xeditable',
    'angular-sanitize': 'node_modules/angular-sanitize/angular-sanitize',
    'angular-ui-bootstrap': 'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-tpls',
    'author': 'js/authors/author',
    bootstrap: 'node_modules/bootstrap-sass/assets/javascripts/bootstrap',
    'bootstrap-datetimepicker': 'node_modules/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker',
    'bootstrap-multiselect': 'node_modules/bootstrap-multiselect/dist/js/bootstrap-multiselect',
    'bucketsjs': 'node_modules/buckets-js/dist/buckets',
    clipboard: 'node_modules/clipboard/dist/clipboard',
    d3: "node_modules/d3/d3",
    'd3-tip': 'node_modules/d3-tip/index',
    'd3wrapper': 'js/d3-wrapper',
    datatables: 'node_modules/datatables.net-bs/js/dataTables.bootstrap',
    'datatables.net': 'node_modules/datatables.net/js/jquery.dataTables',
    feedback: 'js/feedback/feedback',
    flight: 'node_modules/flightjs/build/flight',
    hgn: 'node_modules/requirejs-hogan-plugin/hgn',
    hogan: 'node_modules/hogan.js/web/builds/3.0.2/hogan-3.0.2.amd',
    'holding-pen-module': 'js/inspire_workflows_ui/holdingpen/holdingpen.module',
    'holding-pen-directives': 'js/inspire_workflows_ui/holdingpen/holdingpen.directives',
    'holding-pen-services': 'js/inspire_workflows_ui/holdingpen/holdingpen.services',
    'holding-pen-filters': 'js/inspire_workflows_ui/holdingpen/holdingpen.filters',
    inspirehep: 'node_modules/inspirehep-js/dist/inspirehep',
    'inspirehep-clipboard': 'js/inspire_clipboard',
    'impact-graphs': 'node_modules/impact-graphs/impact-graph',
    'inspirehep-search': 'node_modules/inspirehep-search-js/dist/inspirehep-search',
    'invenio-search': 'node_modules/invenio-search-js/dist/invenio-search-js',
    jquery: 'node_modules/jquery/jquery',
    'jquery.ui': 'node_modules/jquery-ui/jquery-ui',
    moment: 'node_modules/moment/moment',
    'ngclipboard': 'node_modules/ngclipboard/src/ngclipboard',
    'profile': 'js/authors/profile',
    'publications': 'js/authors/publications',
    'readmore': 'node_modules/readmore-js/readmore',
    text: 'node_modules/requirejs-hogan-plugin/text',
    toastr: 'node_modules/toastr/toastr',
    typeahead: 'node_modules/typeahead.js/dist/typeahead.bundle',
    sifter: 'node_modules/sifter/sifter',
    microplugin: 'node_modules/microplugin/src/microplugin'
  },
  shim: {
    angular: {
      exports: 'angular'
    },
    'angular-loading-bar': {
      deps: ['angular']
    },
    'angular-sanitize': {
      deps: ['angular']
    },
    'angular-ui-bootstrap': {
      deps: ['angular']
    },
    'angular-xeditable': {
      deps: ['jquery', 'angular']
    },
    bootstrap: {
      deps: ['jquery', 'jquery.ui']
    },
    'bootstrap-datetimepicker': {
      deps: ['jquery', 'bootstrap', 'moment'],
      exports: '$.fn.datetimepicker'
    },
    'bootstrap-multiselect': {
      deps: ['jquery'],
      exports: '$.fn.multiselect'
    },
    'impact-graphs': {
      deps: ['d3wrapper'],
      exports: 'ImpactGraph'
    },

    'holding-pen-services': {
      deps: ['angular']
    },

    'holding-pen-directives': {
      deps: ['angular', 'holding-pen-services']
    },

    'holding-pen-filters': {
      deps: ['angular']
    },

    'holding-pen-module': {
      deps: ['angular', 'holding-pen-directives', 'holding-pen-filters', 'angular-sanitize']
    },


    'inspirehep': {
      deps: ['angular', 'angular-sanitize', 'angular-ui-bootstrap', 'ngclipboard']
    },
    'inspirehep-search': {
        deps: ['angular', 'angular-sanitize', 'angular-ui-bootstrap', 'ngclipboard']
    },
    'invenio-search': {
        deps: ['angular']
    },
    jquery: {
      exports: '$'
    },
    'ngclipboard': {
        deps: ['angular', 'inspirehep-clipboard', 'clipboard']
    },
    typeahead: {
      deps: ['jquery'],
      exports: 'Bloodhound'
    },
    'jquery.ui': {
        deps: ['jquery']
    }
  }
});
