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
    'flight',
    'datatables',
    'bootstrap'
  ],
  function($, flight) {
      'use strict';

      return flight.component(Datatables);

      function Datatables() {

        this.attributes({
          recid: '',
          endpoint: '',
          citation_count: '',
          seriesname: '',
          cnum: '',
          experiment_name: ''
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
                endpoint: that.attr.endpoint
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#references .datatables-loading").hide();
                $('#references .datatables-wrapper').show();
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
                endpoint: that.attr.endpoint
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#citations .datatables-loading").hide();
                $('#citations .datatables-wrapper').show();
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

          $('#record-institution-people-table').DataTable({
            "bLengthChange": false,
            "bInfo" : false,
            "ajax": {
              "url": "/ajax/institutions/people",
              "data": {
                recid: that.attr.recid
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#record-institution-people .datatables-loading").hide();
                $("#datatables-wrapper ul.pagination").addClass("pagination-sm");
                var total_text = json.data.length + " Authors ";
                $("#record-institution-people .panel-heading").html(total_text);
                $('#record-institution-people .datatables-wrapper').show();
              }
              else {
                $('#record-institution-people .panel-body').text("There are no authors on INSPIRE associated with this institution.").show()
              }
            },
            "aaSorting": [],
            "autoWidth": false,
            // "paging": false,
            "searching": false,
            dom:
              "<'row'<'col-sm-6'l><'col-sm-6'f>>" +
              "<'row'<'col-sm-12'tr>>" +
              "<'row'<'col-sm-12'p>>"
          });

          $('#record-institution-experiments-table').DataTable({
            "bLengthChange": false,
            "bInfo" : false,
            "ajax": {
              "url": "/ajax/institutions/experiments",
              "data": {
                recid: that.attr.recid
              },
              "method": "GET"
              },
              "fnInitComplete": function(oSettings, json) {
                if ( json.data.length > 0 ) {
                  $("#record-institution-experiments .datatables-loading").hide();
                  $("#datatables-wrapper ul.pagination").addClass("pagination-sm");
                  var total_text = json.total + " Experiments ";
                  if ( json.total > json.data.length ) {
                    total_text = total_text + "<span class='record-panel-heading-muted'> Showing newest " + json.data.length + "</span>";
                  }
                  $("#record-institution-experiments .panel-heading").html(total_text);
                  $('#record-institution-experiments .datatables-wrapper').show();
                }
                else {
                  $('#record-institution-experiments .panel-body').text("There are no experiments on INSPIRE associated with this institution.").show()
                }
            },
            "aaSorting": [[1, 'desc']],
            "autoWidth": false,
            // "paging": false,
            "searching": false,
            dom:
              "<'row'<'col-sm-6'l><'col-sm-6'f>>" +
              "<'row'<'col-sm-12'tr>>" +
              "<'row'<'col-sm-12'p>>"
          });

          $('#record-institution-papers-table').DataTable({
            "bLengthChange": false,
            "bInfo" : false,
            "ajax": {
              "url": "/ajax/institutions/papers",
              "data": {
                recid: that.attr.recid
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#record-institution-papers .datatables-loading").hide();
                $("#datatables-wrapper ul.pagination").addClass("pagination-sm");
                var total_text = json.total + " Papers ";
                if ( json.total > json.data.length ) {
                  total_text = total_text + "<span class='record-panel-heading-muted'> Showing newest " + json.data.length + "</span>";
                }
                $("#record-institution-papers .panel-heading").html(total_text);
                $('#record-institution-papers .datatables-wrapper').show();
              }
              else {
                $('#record-institution-papers .panel-body').text("There are no papers on INSPIRE associated with this institution.").show()
              }
            },
            "aaSorting": [],
            "aoColumns": [
            { sWidth: '50%' },
            { sWidth: '20%' },
            { sWidth: '10%' },
            { sWidth: '10%' },
            { sWidth: '10%' }],
            "autoWidth": false,
            // "paging": false,
            "searching": false,
            dom:
              "<'row'<'col-sm-6'l><'col-sm-6'f>>" +
              "<'row'<'col-sm-12'tr>>" +
              "<'row'<'col-sm-12'p>>"
          });

          $('#record-conference-series-table').DataTable({
            language: {
              info: "Showing _START_ to _END_ of _TOTAL_ conferences",
              search: "_INPUT_",
              searchPlaceholder: "Filter conferences..."
            },
            "ajax": {
              "url": "/ajax/conferences/series",
              "data": {
                recid: that.attr.recid,
                seriesname: that.attr.seriesname,
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                var total_text = json.total + " Conferences in the series";
                if ( json.total > json.data.length ) {
                  total_text = total_text + "<span class='record-panel-heading-muted'> Showing newest " + json.data.length + "</span>";
                }
                $('#record-conference-series .panel-heading').html(total_text);
                $("#record-conference-series .datatables-loading").hide();
                $('#record-conference-series .datatables-wrapper').show();
              }
              else {
                $('#record-conference-series .panel-body').text("There are no other conferences in this series.").show()
              }
            },
            "aoColumns": [
            { sWidth: '50%' },
            { sWidth: '20%' },
            { sWidth: '15%' },
            { sWidth: '15%' }],
            "aaSorting": [],
            "autoWidth": false,
            "bLengthChange": false,
            "bInfo" : false,
            "searching": false,
            "bPaginate": false
          });

          $('#record-conference-papers-table').DataTable({
            "bLengthChange": false,
            "bInfo" : false,
            "ajax": {
              "url": "/ajax/conferences/contributions",
              "data": {
                recid: that.attr.recid,
                cnum: that.attr.cnum
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#record-conference-papers .datatables-loading").hide();
                var total_text = json.total + " Contributions ";
                if ( json.total > json.data.length ) {
                  total_text = total_text + "<span class='record-panel-heading-muted'> Showing top " + json.data.length + "</span>";
                }
                $("#record-conference-papers .panel-heading").html(total_text);
                $('#record-conference-papers .datatables-wrapper').show();
              }
              else {
                $('#record-conference-papers .panel-body').text("There are no papers on INSPIRE associated with this conference.").show()
              }
            },
            "aaSorting": [],
            "aoColumns": [
            { sWidth: '50%' },
            { sWidth: '20%' },
            { sWidth: '20%' },
            { sWidth: '10%' }],
            "autoWidth": false,
            "paging": false,
            "searching": false,
            dom:
              "<'row'<'col-sm-6'l><'col-sm-6'f>>" +
              "<'row'<'col-sm-12'tr>>" +
              "<'row'<'col-sm-12'p>>"
          });

          $('#record-experiment-papers-table').DataTable({
            "bLengthChange": false,
            "bInfo" : false,
            "ajax": {
              "url": "/ajax/experiments/contributions",
              "data": {
                recid: that.attr.recid,
                experiment_name: that.attr.experiment_name
              },
              "method": "GET"
            },
            "fnInitComplete": function(oSettings, json) {
              if ( json.data.length > 0 ) {
                $("#record-experiment-papers .datatables-loading").hide();
                var total_text = json.total + " Papers associated with " + that.attr.experiment_name;
                if ( json.total > json.data.length ) {
                  total_text = total_text + "<span class='record-panel-heading-muted'> Showing top " + json.data.length + "</span>";
                }
                $("#record-experiment-papers .panel-heading").html(total_text);
                $('#record-experiment-papers .datatables-wrapper').show();
              }
              else {
                $('#record-experiment-papers .panel-body').text("There are no papers on INSPIRE associated with this experiment.").show()
              }
            },
            "aaSorting": [],
            "aoColumns": [
            { sWidth: '50%' },
            { sWidth: '20%' },
            { sWidth: '20%' },
            { sWidth: '10%' }],
            "autoWidth": false,
            "paging": true,
            "searching": false,
            dom:
              "<'row'<'col-sm-6'l><'col-sm-6'f>>" +
              "<'row'<'col-sm-12'tr>>" +
              "<'row'<'col-sm-12'p>>"
          });

          $('#record-experiment-people-table').DataTable({
        "bLengthChange": false,
        "bInfo" : false,
        "ajax": {
          "url": "/ajax/experiments/people",
          "data": {
            experiment_name: that.attr.experiment_name
          },
          "method": "GET"
        },
        "fnInitComplete": function(oSettings, json) {
          if ( json.data.length > 0 ) {
            $("#record-experiment-people .datatables-loading").hide();
            $("#datatables-wrapper ul.pagination").addClass("pagination-sm");
            var total_text = json.data.length + " Collaboration members";
            $("#record-experiment-people .panel-heading").html(total_text);
            $('#record-experiment-people .datatables-wrapper').show();
          }
          else {
            $('#record-experiment-people .panel-body').text("There are no authors on INSPIRE associated with this experiment.").show()
          }
        },
        "aaSorting": [],
        "autoWidth": false,
        // "paging": false,
        "searching": false,
        dom:
          "<'row'<'col-sm-6'l><'col-sm-6'f>>" +
          "<'row'<'col-sm-12'tr>>" +
          "<'row'<'col-sm-12'p>>"
    });
  });

}});
