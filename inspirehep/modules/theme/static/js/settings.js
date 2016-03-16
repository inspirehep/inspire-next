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
    'angular-sanitize': 'node_modules/angular-sanitize/angular-sanitize',
    'angular-ui-bootstrap': 'node_modules/angular-ui-bootstrap/dist/ui-bootstrap-tpls',
    bootstrap: 'node_modules/bootstrap-sass/assets/javascripts/bootstrap',
    'bootstrap-datetimepicker': 'node_modules/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker',
    'bootstrap-multiselect': 'node_modules/bootstrap-multiselect/dist/js/bootstrap-multiselect',
    clipboard: 'node_modules/clipboard/dist/clipboard',
    feedback: 'js/feedback/feedback',
    flight: 'node_modules/flightjs/build/flight',
    hgn: 'node_modules/requirejs-hogan-plugin/hgn',
    hogan: 'node_modules/hogan.js/web/builds/3.0.2/hogan-3.0.2.amd',
    inspirehep: 'node_modules/inspirehep-js/dist/inspirehep',
    'inspirehep-search': 'node_modules/inspirehep-search-js/dist/inspirehep-search',
    'invenio-search': 'node_modules/invenio-search-js/dist/invenio-search-js',
    jquery: 'node_modules/jquery/jquery',
    moment: 'node_modules/moment/moment',
    text: 'node_modules/requirejs-hogan-plugin/text',
    toastr: 'node_modules/toastr/toastr',
    typeahead: 'node_modules/typeahead.js/dist/typeahead.bundle'
  },
  shim: {
    angular: {
      exports: 'angular'
    },
    'angular-sanitize': {
      deps: ['angular']
    },
    'angular-ui-bootstrap': {
      deps: ['angular']
    },
    bootstrap: {
      deps: ['jquery']
    },
    'bootstrap-datetimepicker': {
      deps: ['jquery', 'bootstrap', 'moment'],
      exports: '$.fn.datetimepicker'
    },
    'bootstrap-multiselect': {
      deps: ['jquery'],
      exports: '$.fn.multiselect'
    },
    'inspirehep': {
      deps: ['angular', 'angular-ui-bootstrap']
    },
    'inspirehep-search': {
        deps: ['angular', 'angular-sanitize']
    },
    'invenio-search': {
        deps: ['angular']
    },
    jquery: {
      exports: '$'
    },
    typeahead: {
      deps: ['jquery'],
      exports: 'Bloodhound'
    }
  }
});
