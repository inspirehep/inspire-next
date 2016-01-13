 /*
  * This file is part of INSPIRE.
  * Copyright (C) 2015 CERN.
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

 define(
  [
    'jquery',
    'flight/lib/component',
    'datatables',
    'bootstrap'
  ],
  function($, defineComponent) {
      'use strict';

      return defineComponent(Datatables);

      function Datatables() {

        this.attributes({
          recid: '',
          collection: ''
        });

        this.after('initialize', function() {
          var that = this;

          $('#record-references-table').DataTable({
            language: {
              search: "_INPUT_",
              searchPlaceholder: "Filter references..."
            },
            "ajax": {
              "url": "/ajax/references",
              "data": {
                recid: that.attr.recid,
                collection: that.attr.collection
              },
              "method": "POST"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#record-references-loading").hide();
                $('#record-references-table-wrapper').show();
              }
              else {
                $('#references .panel-body').text("There are no references available for this record.").show()
              }
            }
          });

          $('#record-citations-table').DataTable({
            language: {
              search: "_INPUT_",
              searchPlaceholder: "Filter citations..."
            },
            "ajax": {
              "url": "/ajax/citations",
              "data": {
                recid: that.attr.recid,
                collection: that.attr.collection
              },
              "method": "POST"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#record-citations-loading").hide();
                $('#record-citations-table-wrapper').show();
              }
              else {
                $('#citations .panel-body').text("There are no citations available for this record.").show()
              }
            }
          });
      });

    }
      
});
