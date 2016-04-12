/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
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
* In applying this license, CERN does not
* waive the privileges and immunities granted to it by virtue of its status
* as an Intergovernmental Organization or submit itself to any jurisdiction.
*/

define(['publications'], function(Publications) {
  var app = angular.module('publications', ['profile']);

  app.directive('biography', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<ul class="categories">' +
                '<li ng-repeat="category in categories">' +
                '<a href="/search?p=keyword:{{ category }}">' +
                '{{ category }}</a></li></ul>',
      scope: true,
      link: function(scope) {
        scope.$watch('publications', function() {
          var categories = scope.publications.keywords;
          scope.categories = categories.slice(0, 25);          
        });
      }
    };
  });

  app.directive('statisticsChart', function($parse) {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<div id="plot"></div>',
      scope: true,
      link: function(scope, element, attrs) {
        scope.$watch('statistics', function() {
          // Data.
          var publicationsDataToPlot = scope.statistics[0];

          var drawBarChart = function(width) {
            var margins = 40;
            var width = getDivWidth() - margins;
            var height = 220 - 2 * margins;

            var svg = d3.select('#plot').append("svg")
                .attr("width", width)
                .attr("height", height + 2 * margins)
              .append("g")
                .attr("transform", "translate(" + margins + "," + margins + ")");

            var date_parser = d3.time.format("%Y").parse
            var year_extent = d3.extent(publicationsDataToPlot, function(d) {
                return d.year;
              });

            var bar_width = width / (year_extent[1] - year_extent[0]) / 4;

            yearScale = d3.time.scale()
              .domain([date_parser(String(year_extent[0]-1)),
                date_parser(String(year_extent[1]+1))]).range([0, width - (margins * 2)]);

            publicationsScale = d3.scale.linear()
              .domain([0, d3.max(publicationsDataToPlot, function(d) {
                return d.publications;
              })])
              .range([0, height]);

            publicationsScaleAxis = d3.scale.linear()
              .domain([d3.max(publicationsDataToPlot, function(d) {
                return d.publications;
              }), 0])
              .range([0, height]);

            yearAxis = d3.svg.axis()
              .scale(yearScale)
              .orient("bottom")
              .tickSize(0)
              .tickPadding(12)
              .tickFormat(d3.time.format("%Y"));

            publicationsAxis = d3.svg.axis()
              .scale(publicationsScaleAxis)
              .orient("left")
              .tickSize(0)
              .tickPadding(8)
              .ticks(4);

            svg.append("svg:g")
              .attr("class", "xAxis axis")
              .attr("transform", "translate(0," + (height) +")")
              .call(yearAxis);

            svg.append("svg:g")
              .attr("class", "yAxis axis")
              .attr("transform", "translate(0, 0)")
              .call(publicationsAxis);

            svg.append("text")
              .attr("class", "publicationsLabel")
              .attr("text-anchor", "end")
              .attr("x", -22)
              .attr("y", -30)
              .attr("transform", "rotate(-90)")
              .text("Research works");

            svg.append("text")
              .attr("class", "citationsLabel")
              .attr("text-anchor", "end")
              .attr("x", 95)
              .attr("y", -width+50)
              .attr("transform", "rotate(-270)")
              .text("Citations");

            svg.selectAll("publications")
                .data(publicationsDataToPlot)
              .enter().append("rect")
                .style("fill", "rgb(13, 131, 183)")
                .attr("x", function(d) { 
                  return yearScale(date_parser(String(d.year))) - bar_width; })
                .attr("width", bar_width)
                .attr("y", height)
                .attr("height", 0)
                .transition()
                  .duration(1000)
                  .attr("y", function(d) {
                    return (height) - publicationsScale(d.publications); })
                  .attr("height", function(d) { 
                    return publicationsScale(d.publications); })
          }

          var getDivWidth = function() {
            // Example: 570px.
            var width_str = d3.select('#statistics-chart').style('width');
            width_str = width_str.slice(0, -2);

            return parseInt(width_str);
          }

          var resizeListener = function() {
            d3.select("#statistics-chart").selectAll("svg").remove();

            if (publicationsDataToPlot.length != 0) {
              drawBarChart();
            }
          }

          // Event handlers.
          if (window.attachEvent) {
            // Internet Explorer.
            window.attachEvent('onresize', resizeListener);
          }
          else if (window.addEventListener) {
            window.addEventListener('resize', resizeListener, true);
          }
          else {
            // The webbrowser does not support JavaScript event binding.
            var alert_text = "You are using an outdated browser. " +
                             "Please upgrade your browser to improve " +
                             "your experience.";
            alert(alert_text);
          }

          // Initial graph.
          if (publicationsDataToPlot.length != 0) {
            drawBarChart();
          }
        });
      }
    };
  });

  app.directive('collaborators', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/collaborators.html',
      scope: false,
    };
  });

  app.directive('publicationsList', function($timeout) {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/publications.html',
      scope: true,
      link: function(scope, element) {
        scope.$watch('publications', function() {
          scope.publicationsList = scope.publications.publications;

          // Inject DataTable.
          $timeout(function() {
            if (scope.publicationsList.length > 0) {
              $('#publications-table').DataTable( {
                'bFilter': false,
                'bLengthChange': false,
                'info' : false,
                // In case of enabled search box.
                'oLanguage': {
                  'sSearch': '<i class="fa fa-search" aria-hidden="true"></i>'
                 }
              });
            }
          }, 0);
        });
      }
    };
  });

  app.directive('statistics', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/statistics.html',
      scope: true,
      link: function(scope) {
        scope.$watch('statistics', function() {
          scope.count = scope.statistics[1];
          scope.researchWorks = scope.statistics[2];
        });
      }
    };
  });
});
