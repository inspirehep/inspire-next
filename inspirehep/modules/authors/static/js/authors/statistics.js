/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
 *
 * INSPIRE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

define(['statistics'], function(Profile) {
  var app = angular.module('statistics', ['profile']);

  app.directive('statisticsChart', function($parse) {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<div id="statistics-plot"></div>',
      scope: true,
      link: function(scope, element, attrs) {
        scope.$watch('statistics', function() {
          // Count publications, must be in {year: YYYY, publications: X} format.
          publicationsCount = {}
          publicationsStats = []
          yearStats = []

          angular.forEach(scope.publications, function(publication) {
            year = new Date(publication.date).getFullYear();

            if (publicationsCount.hasOwnProperty(year)) {
              publicationsCount[year]++;
            }
            else {
              publicationsCount[year] = 1;
            }
          });

          for (var year in publicationsCount) {
            publicationsStats.push({
              year: parseInt(year),
              publications: publicationsCount[year]
            });

            yearStats.push({
              year: parseInt(year)
            });
          }

          // Count citations.
          citationsCount = {}
          citationsStats = []

          angular.forEach(scope.citations, function(citations) {
            angular.forEach(citations.citers, function(citation) {
              year = new Date(citation.date).getFullYear();

              if (citationsCount.hasOwnProperty(year)) {
                citationsCount[year]++;
              }
              else {
                citationsCount[year] = 1;
              }
            });
          });

          for (var year in citationsCount) {
            citationsStats.push({
              year: parseInt(year),
              citations: citationsCount[year]
            });

            yearStats.push({
              year: parseInt(year)
            });
          }

          // Logic.
          var drawBarChart = function(width) {
            var margins = 40;
            var width = getDivWidth() - margins;
            var height = 220 - 2 * margins;

            var svg = d3.select('#statistics-plot').append("svg")
                .attr("width", width)
                .attr("height", height + 2 * margins)
              .append("g")
                .attr("transform", "translate(" + margins + "," + margins + ")");

            var date_parser = d3.time.format("%Y").parse
            var year_extent = d3.extent(yearStats, function(d) {
                return d.year;
              });

            var bar_width = width / (year_extent[1] - year_extent[0]) / 4;

            yearScale = d3.time.scale()
              .domain([date_parser(String(year_extent[0]-1)),
                date_parser(String(year_extent[1]+1))]).range([0, width - (margins * 2)]);

            citationsScale = d3.scale.linear()
              .domain([0, d3.max(citationsStats, function(d) {
                return d.citations;
              })])
              .range([0, height]);

            publicationsScale = d3.scale.linear()
              .domain([0, d3.max(publicationsStats, function(d) {
                return d.publications;
              })])
              .range([0, height]);

            citationsScaleAxis = d3.scale.linear()
              .domain([d3.max(citationsStats, function(d) {
                return d.citations;
              }), 0])
              .range([0, height]);

            publicationsScaleAxis = d3.scale.linear()
              .domain([d3.max(publicationsStats, function(d) {
                return d.publications;
              }), 0])
              .range([0, height]);

            yearAxis = d3.svg.axis()
              .scale(yearScale)
              .orient("bottom")
              .tickSize(0)
              .tickPadding(12)
              .tickFormat(d3.time.format("%Y"));

            citationsAxis = d3.svg.axis()
              .scale(citationsScaleAxis)
              .orient("right")
              .tickSize(0)
              .tickPadding(8)
              .ticks(4);

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
              .attr("class", "citationsAxis axis")
              .attr("transform", "translate(" + (width - 2 * margins) + ", 0)")
              .call(citationsAxis);

            svg.append("svg:g")
              .attr("class", "publicationsAxis axis")
              .attr("transform", "translate(0, 0)")
              .call(publicationsAxis);

            svg.append("text")
              .attr("class", "citationsLabel")
              .attr("text-anchor", "end")
              .attr("x", 103)
              .attr("y", -width+50)
              .attr("transform", "rotate(-270)")
              .text("Citations");

            svg.append("text")
              .attr("class", "publicationsLabel")
              .attr("text-anchor", "end")
              .attr("x", -22)
              .attr("y", -30)
              .attr("transform", "rotate(-90)")
              .text("Research works");

            svg.selectAll("publications")
                .data(publicationsStats)
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

            svg.selectAll("citations")
                .data(citationsStats)
              .enter().append("rect")
                .style("fill", "rgb(44, 62, 80)")
                .attr("x", function(d) {
                  return yearScale(date_parser(String(d.year))); })
                .attr("width", bar_width)
                .attr("y", height)
                .attr("height", 0)
                .transition()
                  .duration(1000)
                  .attr("y", function(d) {
                    return (height) - citationsScale(d.citations); })
                  .attr("height", function(d) {
                    return citationsScale(d.citations); })
          }

          // Get the total width of the div, where the chart is placed.
          var getDivWidth = function() {
            // Example: 570px.
            var width_str = d3.select('#statistics-chart').style('width');
            width_str = width_str.slice(0, -2);

            return parseInt(width_str);
          }

          // Listen for changes in the width of the website.
          var resizeListener = function() {
            d3.select("#statistics-chart").selectAll("svg").remove();

            if (Object.keys(publicationsCount).length !== 0) {
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
          if (Object.keys(publicationsCount).length !== 0) {
            drawBarChart();
          }
        });
      }
    };
  });

  app.directive('statisticsSummary', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/statistics.html',
    };
  });
});
