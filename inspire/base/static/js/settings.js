/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014 CERN.
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
  baseUrl: "/",
  paths: {
    jquery: "vendors/jquery/dist/jquery",
    ui: "vendors/jquery-ui/ui",
    "jqueryui-timepicker": "vendors/jqueryui-timepicker-addon/dist",
    "jquery-form": "vendors/jquery-form/jquery.form",
    hgn: "vendors/requirejs-hogan-plugin/hgn",
    hogan: "vendors/hogan/web/builds/3.0.2/hogan-3.0.2.amd",
    text: "vendors/requirejs-hogan-plugin/text",
    flight: "vendors/flight",
    typeahead: "vendors/typeahead.js/dist/typeahead.bundle",
    "bootstrap-select": "js/bootstrap-select",
    "jquery-caret": "vendors/jquery.caret/dist/jquery.caret-1.5.2",
    "jquery-tokeninput": "vendors/jquery-tokeninput/src/jquery.tokeninput",
    "jquery-jeditable": "vendors/jquery.jeditable/index",
    "moment": "vendors/moment/moment",
    "datatables": "vendors/datatables/media/js/jquery.dataTables",
    "datatables-plugins": "vendors/datatables-plugins/integration/bootstrap/3/dataTables.bootstrap",
    "datatables-tabletools": "vendors/datatables-tabletools/js/dataTables.tableTools",
    "bootstrap-datetimepicker": "vendors/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker",
    "bootstrap-tagsinput": "vendors/bootstrap-tagsinput/src/bootstrap-tagsinput",
    bootstrap: "vendors/bootstrap/dist/js/bootstrap",
    prism: "vendors/prism/prism",
    d3: "vendors/d3/d3.js",
    "jasmine-jquery": "vendors/jasmine-jquery/lib/jasmine-jquery",
    "jasmine-core": "vendors/jasmine/lib/jasmine-core/jasmine",
    "jasmine-html": "vendors/jasmine/lib/jasmine-core/jasmine-html",
    "jasmine-ajax": "vendors/jasmine-ajax/lib/mock-ajax",
    "jasmine-flight": "vendors/jasmine-flight/lib/jasmine-flight",
    "jasmine-boot": "js/jasmine/boot",
    "searchtypeahead-configuration": "js/search/default_typeahead_configuration",
    "jasmine-events": "js/jasmine/events_checker",
    "jasmine-initialization": "js/jasmine/initialization_checker",
    // INSPIRE
    "bootstrap-multiselect": "vendors/bootstrap-multiselect/dist/js/bootstrap-multiselect",
    "readmore": "vendors/readmore/readmore",
    "buckets": "vendors/buckets/buckets",
    "feedback": "vendors/feedback/examples/js/feedback",
    "html2canvas": "vendors/html2canvas/build/html2canvas",
    "highcharts": "vendors/highcharts-release/highcharts"
  },
  shim: {
    jquery: {
      exports: "$"
    },
    d3: {
      exports: "d3"
    },
    "jqueryui-timepicker/jquery-ui-sliderAccess": {
      deps: ["jquery"]
    },
    "jqueryui-timepicker/jquery-ui-timepicker-addon": {
      deps: ["jquery",
        "ui/slider"
      ]
    },
    "jqueryui-timepicker/i18n/jquery-ui-timepicker-addon-i18n": {
      deps: ["jqueryui-timepicker/jquery-ui-timepicker-addon"]
    },
    typeahead: {
      deps: ["jquery"],
      exports: "Bloodhound"
    },
    "bootstrap-select": {
      deps: ["jquery"],
      exports: "$.fn.buttonSelect"
    },
    "jquery-caret": {
      deps: ["jquery"],
      exports: "$.fn.caret"
    },
    "jquery-tokeninput": {
      deps: ["jquery"],
      exports: "$.fn.tokenInput"
    },
    "jquery-jeditable": {
      deps: ["jquery"],
      exports: "$.fn.editable"
    },
    "bootstrap-tagsinput": {
      deps: ["jquery"],
      exports: "$.fn.tagsinput"
    },
    "datatables": {
      deps: ["jquery"],
      exports: "$.fn.dataTable"
    },
    bootstrap: {
      deps: ["jquery"]
    },
    "datatables-plugins": {
      deps: ["jquery", "bootstrap", "datatables"]
    },
    "datatables-tabletools": {
      deps: ["jquery", "datatables"],
      exports: "$.fn.dataTable.TableTools"
    },
    "bootstrap-datetimepicker": {
      deps: ["jquery", "bootstrap", "moment"],
      exports: "$.fn.datetimepicker"
    },
    prism: {
      exports: "Prism"
    },
    "jasmine-core": {
      exports: "jasmineRequire"
    },
    "jasmine-boot": {
      exports: "jasmine",
    },
    "jasmine-jquery": {
      deps: ["jquery", "jasmine-boot"],
      exports: "jasmine",
    },
    "jasmine-ajax": {
      deps: ["jasmine-boot"],
      exports: "jasmine",
    },
    "jasmine-html": {
      deps: ["jasmine-core"],
      exports: "jasmineRequire"
    },
    "jasmine-flight": {
      deps: ["jasmine-boot", "jasmine-jquery"],
      exports: "jasmine",
    },
    "vendors/jasmine/lib/jasmine-core/boot": {
      deps: ["jasmine-html"],
      exports: "window.onload",
    },
    "jasmine-events": {
      deps: ["jasmine-jquery"],
      exports: "jasmine.EventsChecker",
    },
    "jasmine-initialization": {
      deps: ["jasmine-boot"],
    },
    // INSPIRE
    "bootstrap-multiselect": {
      deps: ["jquery"],
      exports: "$.fn.multiselect"
    },
    "readmore": {
      deps: ["jquery"],
      exports: "$.fn.readmore"
    },
    "html2canvas" : {
      deps: ["jquery"]
    },
    "feedback" : {
      deps: ["jquery", "html2canvas"],
       exports: "Feedback"
    },
    "highcharts" : {
      deps: ["jquery"],
      exports: "Highcharts"
    },
  }
});
