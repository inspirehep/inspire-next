/**
This file is part of INSPIRE.
Copyright (C) 2015 CERN.

INSPIRE is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

INSPIRE is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
**/
define(function(require) {
  'use strict';

  var toggles = null;

  $ = require("jquery");
  // TO DO replace flot with more reliable library
  require("jquery.flot");
  require("jquery.flot.axislabels");
  require("jquery.flot.tooltip");
  require("jquery.flot.orderbars");
  require("jquery.flot.resize");
  require("growraf");
  require("js/translate");
  var Hogan = require("hogan");
  var tpl_table = require('hgn!../templates/statstable');

  var profileStats = require('flight/lib/component')(function() {

    this.plot = null;
    this.ranges = null;

    this.convertDictForGraph = function(dict) {
      /**
       * .. js:function:: convertDictForGraph(dict)
       *
       *    Get list of tuples from dict.
       *
       *    :param dict: dictionary in form of (year: quantity)
       *
       *    :return: list of tuples in form of (year, quantity)
       */
      var result = [];
      for (var i = 0; i <= this.ranges.maxYear - this.ranges.minYear;
        result[i] = [i + this.ranges.minYear, dict[i + this.ranges.minYear]],
        i++);
      return result;
    };

    this.createGraph = function(citations) {
      /**
       * .. js:function:: createGraph(citations)
       *
       *    Compute bars and display the graph.
       *
       *    :param citations: dictionary with all applicable citations for
       *                      given author as keys and years as values
       */
      var citationData = new Object();
      for (var i = this.ranges.minYear; i <= this.ranges.maxYear;
        citationData[i] = 0, i++);
      var paperData = $.extend(true, {}, citationData);

      // Group citations and papers by year
      $.each(citations, function(index, value) {
        ++citationData[value];
      });
      $.each(this.shownWorks, function(index, value) {
        ++paperData[value.year];
      });

      citationData = this.convertDictForGraph(citationData);
      paperData = this.convertDictForGraph(paperData);

      this.dataset = [{
        label: "Citations",
        data: citationData,
        yaxis: 2,
        color: "rgb(33,33,33)",
        bars: {
          order: 2,
          barWidth: 0.45,
          lineWidth: 0
        }
      }, {
        label: "Papers",
        data: paperData,
        yaxis: 1,
        color: "rgb(66, 139, 202)",
        bars: {
          order: 1,
          barWidth: 0.45,
          lineWidth: 0
        }
      }];

      // Don't show ticks which are not integer numbers
      var axisFormatter = function(number, object) {
        if (number % 1 === 0)
          return number;
        return "";
      }

      this.options = {
        xaxis: {
          // Add a bit of space on both borders to display both relevant bars
          min: this.ranges.maxYear - 11,
          max: this.ranges.maxYear + 1,
          tickLength: 0,
          tickFormatter: axisFormatter
        },
        series: {
          bars: {
            show: true,
          },
          grow: {
            active: true,
            duration: 250
          }
        },
        yaxes: [{
          position: "left",
          axisLabel: "Papers",
          tickLength: 0,
          tickFormatter: axisFormatter,
          axisLabelUseCanvas: true,
          axisLabelFontSizePixels: 10,
          axisLabelPadding: 10,
          min: 0,
          max: this.ranges.maxPapers
        }, {
          position: "right",
          axisLabel: "Citations",
          tickLength: 0,
          tickFormatter: axisFormatter,
          axisLabelUseCanvas: true,
          axisLabelFontSizePixels: 10,
          axisLabelPadding: 10,
          min: 0,
          max: this.ranges.maxCitations
        }],
        legend: {
          backgroundColor: '#fff',
          position: "nw"
        },
        grid: {
          hoverable: true,
          borderWidth: {
            top: 0,
            left: 1,
            right: 1,
            bottom: 1
          },
          mouseActiveRadius: 50,
          axisMargin: 20
        },
        tooltip: true,
        tooltipOpts: {
          content: function(label, xval, yval, flotItem) {
            return yval + " " + label.toLowerCase() + " in " + xval;
          }
        }
      };

      if (!this.plot)
        // First run
        this.plot = $.plot($("#citation-chart"), this.dataset, this.options);
      else {
        this.plot.setData(this.dataset);
        this.plot.setupGrid();
        this.plot.draw();
      }
    };

    this.h_index = function(citationNumbers) {
      /**
       * .. js:function:: h_index(citationNumbers)
       *
       *    Compute h_index of given author.
       *
       *    :param citationNumbers: list of numbers of citations. Each item
       *                            corresponds to a single paper.
       *
       *    :return: h index
       */
      citationNumbers = citationNumbers.sort(function(a, b) {
        return b - a
      });
      var hindex = null;

      // Compute h-index
      $.each(citationNumbers, function(index, value) {
        if (index + 1 > value) {
          hindex = index;
          return false;
        }
      });
      if (!hindex && hindex !== 0)
      // There were no papers with less than h citations in the table.
        hindex = this.papersNum;

      return hindex;
    }

    this.trigger_toggle = function(event, args) {
      /**
       * .. js:function:: trigger_toggle(event, args)
       *
       *    Redraw the graph and recompute the stats.
       *
       *    :param event: toggleChanged event
       *    :param args: dictionary with works, ranges for the graph and
       *                 current toggles values
       */
      toggles = args.toggles;
      this.shownWorks = args.works;

      this.ranges = args.ranges;

      this.papersNum = this.shownWorks.length;

      var citations = {};
      var citationNumbers = [];
      //var claimedNum = 0;
      var datasetsNum = 0;

      var paperTypes = {
        'published': 0,
        'book': 0,
        'conference': 0,
        'introductory': 0,
        'lecture': 0,
        'thesis': 0,
        'review': 0,
        'proceeding': 0
      };

      // Compute everything in one loop
      $.each(this.shownWorks, function(index, value) {

        //if( value.claimed )
        //  ++claimedNum;

        var papersCitations = 0;
        $.each(value.cited, function(jindex, citation) {

          // Add citations if new are present
          if (!(citation.id in citations)) {

            if (toggles['selfcited-checkbox'])
              citations[citation.id] = citation.year;
            else if (!citation.selfcitation) {
              citations[citation.id] = citation.year;
            }

          }

          // Add number of citations for h-index
          if (toggles['selfcited-checkbox'])
            ++papersCitations;
          else if (!citation.selfcitation)
            ++papersCitations;
        });

        $.each(Object.keys(paperTypes), function(index, paperType) {
          if (value[paperType]) {
            ++paperTypes[paperType];
          }
        })

        citationNumbers[citationNumbers.length] = papersCitations;

        if (value.type === "Data") {
          ++datasetsNum;
        }

      });

      this.createGraph(citations);

      // Fill the table

      //$('#claimed-ratio').html(claimedNum + "/" + this.papersNum + " ");

      // TO DO - add links
      this.$node.find("#citations-num").html("<a href=TODO>" + Object.keys(citations).length + "</a>");
      this.$node.find("#papers-num").html("<a href=TODO>" + this.papersNum + "</a>");

      // Show the h-index
      this.$node.find("#hindex").html(this.h_index(citationNumbers));

      // paperStats renders indented rows
      var paperStats = $.map(paperTypes, function(value, key) {
        if (value > 0)
          return {
            name: key,
            // TO DO - add links
            link: "",
            value: value
          }
      });

      // Always show information about datasets
      paperStats[paperStats.length] = {
        name: 'datasets',
        // TO DO - add links
        link: "",
        value: datasetsNum
      }

      // Remove dynamically added rows
      var rows = this.$node.find(".text-stats > table > tbody > tr");
      $.each(rows, function(index, value) {
        if (value.children[0].textContent.startsWith(" "))
          value.remove();
      });

      this.$node.find(".text-stats > table > tbody").append(tpl_table({
        stats: paperStats,
        translate: function(lambda) {
          return function(text){
            return $._(Hogan.compile(text).render(this));
          }
        }
      }));

    };

    this.show_modal = function(event) {
      /**
       * .. js:function:: show_modal(event)
       *
       *    Show the whole graph in a modal if it was clicked.
       *
       *    :param event: onClick event
       */
      if(!(event.originalEvent.target.localName === 'canvas'))
        // It wasn't the chart that was clicked.
        return;
      $('#graphModal').modal('show');
      var options = $.extend(true, {}, this.options);

      // Show every paper and citation
      options.xaxis.min = this.ranges.minYear - 2;
      var copiedDataset = $.extend(true, [], this.dataset)
      $.plot($("#big-graph"), copiedDataset, options);
    };

    this.after('initialize', function() {
      this.on(document, 'toggleChanged', this.trigger_toggle);
      this.on('click', this.show_modal);
    });
  });


  return profileStats;
});
