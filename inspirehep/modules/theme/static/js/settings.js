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
  baseUrl: "/static/",
  paths: {
    jquery: "node_modules/jquery/jquery",
    bootstrap: "node_modules/bootstrap-sass/assets/javascripts/bootstrap",
    angular: "node_modules/angular/angular",
    "angular-sanitize": "node_modules/angular-sanitize/angular-sanitize",
    "invenio-search": "node_modules/invenio-search-js/dist/invenio-search-js",
    "inspire-search": "js/search/inspire-search",
    hgn: "node_modules/requirejs-hogan-plugin/hgn",
    hogan: "node_modules/hogan.js/web/builds/3.0.2/hogan-3.0.2.amd",
    text: "node_modules/requirejs-hogan-plugin/text",
    flight: "node_modules/flightjs/build/flight",
    typeahead: "node_modules/typeahead.js/dist/typeahead.bundle",
    "moment": "node_modules/moment/moment",
    "bootstrap-datetimepicker": "node_modules/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker",
    "bootstrap-multiselect": "node_modules/bootstrap-multiselect/dist/js/bootstrap-multiselect",
    "feedback": "js/feedback/feedback",
    "toastr": "node_modules/toastr/toastr",
    "clipboard": "node_modules/clipboard/dist/clipboard"
  },
  shim: {
    angular: {
      exports: 'angular'
    },
    jquery: {
      exports: "$"
    },
    bootstrap: {
      deps: ["jquery"]
    },
    typeahead: {
      deps: ["jquery"],
      exports: "Bloodhound"
    },
    "bootstrap-datetimepicker": {
      deps: ["jquery", "bootstrap", "moment"],
      exports: "$.fn.datetimepicker"
    },
    "bootstrap-multiselect": {
      deps: ["jquery"],
      exports: "$.fn.multiselect"
    },
    "invenio-search": {
        deps: ["angular"]
    },
    "inspire-search": {
        deps: ["angular"]
    }
  }
});
