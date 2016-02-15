/*
* This file is part of INSPIRE.
* Copyright (C) 2015, 2016 CERN.
*
* INSPIRE is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation; either version 2 of the
* License, or (at your option) any later version.
*
* INSPIRE is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
* General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
* 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
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
          collection: '',
          citation_count: ''
        });

        this.after('initialize', function() {
          var that = this;

          $('#record-references-table').DataTable({
            language: {
              info: "Showing _START_ to _END_ of _TOTAL_ references",
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
            },
            "aaSorting": [],
            "autoWidth": false
          });

          $('#record-citations-table').DataTable({
            language: {
              info: "Showing _START_ to _END_ of " + that.attr.citation_count + " citations"
            },
            "bPaginate": false,
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
            },
            "aaSorting": [],
            "autoWidth": false,
            "paging": false,
            "searching": false
          });
      });

    }
      
});
