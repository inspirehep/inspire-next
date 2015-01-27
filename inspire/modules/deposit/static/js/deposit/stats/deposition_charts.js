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

define(function(require, exports, module) {

  var $ = require("jquery");
  var tpl_flash_message = require('hgn!js/deposit/templates/flash_message');

  function massageColumnData(data) {
    var series = [];
    for(var i in data) { 
      series.push({name: data[i].name,
                   data: data[i].data});
    }

    return series;
  };

  function DepositionChart(options) {

    this.title = options.title;
    this.subtitle = options.subtitle ?
      options.subtitle : "";
    this.type = options.type ?
      options.type : "pie";

    this.categories = options.categories ?
      options.categories : ["empty"];

    this.data = options.data ?
      options.data : [['empty', 1]];

    this.pie_options = {
      chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false
      },
      title: {
        text: this.title
      },
      tooltip: {
        pointFormat: "<b>{point.percentage:.1f}% ({point.y})</b>"
      },
      plotOptions: {
        pie: {
          allowPointSelect: true,
          cursor: "pointer",
          dataLabels: {
            enabled: true,
            format: "<b>{point.name}</b>: {point.percentage:.1f} % ({point.y})",
            style: {
              color: "black"
            },
            connectorColor: "silver"
          }
        }
      },
      series: [{
        type: this.type,
        name: "Depositions",
        data: this.data
      }]
    };

    this.column_options = {
      chart: {
          type: 'column'
      },
      title: {
          text: this.title
      },
      subtitle: {
          text: this.subtitle
      },
      xAxis: {
          categories: this.categories
      },
      yAxis: {
          min: 0,
          title: {
              text: 'Times filled by users'
          }
      },
      plotOptions: {
          column: {
              pointPadding: 0.2,
              borderWidth: 0
          }
      },
      series: massageColumnData(this.data)
    };
  }

  DepositionChart.prototype = {
    init: function(data){
      var chart_options = {
        title: "Submitted depositions",
        type: "column",
        data: data.columns_deposition_data,
        categories: data.metadata_categories
      };

      $deposition_charts.highcharts(
        new DepositionChart(chart_options).generate()
      );
    },

    update: function(data){
      if(Object.keys(data.deposition_data).length > 0){
        var chart_type = $chart_type.val();
        var chart_data = ((chart_type === "column") ?
          data.columns_deposition_data : data.overall_depositions.pie);

        var chart_options = {
          title: "Submitted depositions",
          type: chart_type,
          data: chart_data
        };

        if(chart_type === "column") {
          chart_options.categories = (data.metadata_categories === '') ?
            ['empty'] : data.metadata_categories;
        }

        $include_hidden.show();
        $deposition_charts.empty();
        $deposition_charts.highcharts(
          new DepositionChart(chart_options).generate()
        );
      } else {
        $include_hidden.hide();
        $deposition_charts.html(tpl_flash_message({
          state: 'info',
          message: "There are no depositions for the given date."
        }));
      }
    },

    filter: function(url){
      var since_date = $('#since_date').val();
      var until_date = $('#until_date').val();
      var params = {};

      if(since_date !== "")
        params.since_date = since_date;
      if(until_date !== "")
        params.until_date = until_date;
      if($include_hidden.hasClass("active"))
        params.include_hidden = true;

      $.ajax({
        url: url,
        data: params
      })
        .done(function(data) {
          var charts_data = {
            deposition_data: data.stats,
            overall_depositions: data.overall_metadata,
            columns_deposition_data: data.metadata_for_column,
            metadata_categories: data.metadata_categories,
          }
          $deposition_charts.empty();
          new DepositionChart({}).update(charts_data);
          if(Object.keys(charts_data.deposition_data).length > 1){
            $('div[id^="chart-"]').parents('.row').show();
            new DepositionChart({}).generate_individual(charts_data);
          } else {
            $('div[id^="chart-"]').parents('.row').hide();
          }
        });
    },

    reset_filter: function(url){
      $('#since_date').val('');
      $('#until_date').val('');

      this.filter(url);
    },

    generate: function(){
      if(this.type === "pie")
        return this.pie_options;
      if(this.type === "column")
        return this.column_options;
    },

    generate_individual: function(data){
      $.each(data.deposition_data, function(name, values){
        $('#chart-'+name).highcharts(
          new DepositionChart({
            title: name + " submissions",
            type: "pie",
            data: values
          }).generate()
        )
      });
    },

    radial_colors: function(){
      colors = Highcharts.map(Highcharts.getOptions().colors, function (color) {
                          return {
                            radialGradient: { cx: 0.5, cy: 0.3, r: 0.7 },
                            stops: [
                                [0, color],
                                [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
                            ]
                          };
                        });
      return colors;
    }
  }

  module.exports = DepositionChart;
});
