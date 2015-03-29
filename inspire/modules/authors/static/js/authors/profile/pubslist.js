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

  require('datatables');
  require('datatables-bootstrap3');
  require('datatables-responsive')
  $ = require('jquery');

  // An exceptional "global" for self-cited. The value is used in the
  // callback passed to datatables
  var self_cited = false;

  var pubsList = require('flight/lib/component')(function() {

    // Represents the list of the publications. Works also as a paper storage
    // that sends all the needed data to other components.

    /**
     * .. js:attribute:: contentType
     *
     *    The type of the content that is shown in the table. By default it shows
     *    papers.
     */
    this.contentType = "papers";

    this.computeRanges = function() {
      /**
       * .. js.function:: computeRanges()
       *
       *    Compute maximum values for the graph ranges and the range of the
       *    x axis.
       *
       *    :returns: Dictionary containing the date range, maximal number of
       *              papers per year and maximal number of citations per year
       */

      // dictionary in form of (year, number of papers)
      var papers = {};

      // dictionary in form of (year, dict(id of citation, bool))
      var citations = {};

      var minYear = 2500;
      var maxYear = 0;

      // fill the dictionaries
      for (var i = 0; i < this.internalPapers.length; i++) {
        minYear = Math.min(minYear, this.internalPapers[i].year);
        maxYear = Math.max(maxYear, this.internalPapers[i].year);

        for (var j = 0; j < this.internalPapers[i].cited.length; j++) {

          var citation = this.internalPapers[i].cited[j];
          if (!(citation.year in citations))
            citations[citation.year] = {};
          citations[citation.year][citation.id] = true;
          maxYear = Math.max(maxYear, citation.year);

        };

        if (this.internalPapers[i].year in papers)
          ++papers[this.internalPapers[i].year];
        else
          papers[this.internalPapers[i].year] = 1;
      };

      var maxCitations = 0;
      var maxPapers = 0;

      $.each(papers, function(key, value) {
        maxPapers = Math.max(value, maxPapers);
      })
      $.each(citations, function(key, value) {
        maxCitations = Math.max(Object.keys(value).length, maxCitations);
      })

      return {
        maxCitations: maxCitations,
        maxPapers: maxPapers,
        minYear: minYear,
        maxYear: maxYear
      }
    }

    this.getIdsFromToggles = function() {
      /**
       * .. js.function:: getIdsFromToggles()
       *
       *    Query the search engine in order to get the list of the papers
       *    that should be displayed and included in the statistics.
       *
       *    :returns: List of integer ids of the records which should be shown.
       */

      // TO DO - hardcoded for mockup
      // implement using search engines queries.
      /*var all = [1219330,
        1216295,
        1115482,
        1094521,
        926899,
        901059,
        846927,
        839428,
        838714,
        832224,
        1176500,
        1176498,
        1176496,
        1176494,
        1176492,
        1176491,
        1176489,
        1176488,
        1176486,
        1176484
      ];
      var not_collabs = [926899, 832224];
      var arxiv = [1115482, 839428, 838714];
      var single_authored = [832224];
      if (!this['collaboration-checkbox'])
        all = not_collabs;
      if (!this['arxiv-checkbox'])
        all = $(all).not(arxiv).get();
      if (!this['singleauthored-checkbox'])
        all = $(all).not(single_authored).get();
      return all;*/

      return [];
    }

    this.unionIds = function(sortedIds, sortedTempWorks) {
      /**
       * .. js.function:: unionIds(sortedIds, sortedTempWorks)
       *
       *    Make a union beetween a list of works and a list of ids.
       *    Complexity: O(n + m).
       *
       *    :param sortedIds: list of ids, sorted.
       *    :param sortedTempWorks: list of works, sorted by id.
       *
       *    :returns: list of works which ids are included on both arguments.
       */
      var otherIndex = 0;
      var shownWorks = [];
      for (var index = 0; index < sortedTempWorks.length; ++index) {
        var currentId = parseInt(sortedTempWorks[index].id);
        while (currentId > sortedIds[otherIndex]) {
          ++otherIndex;
          if (otherIndex === sortedIds.length)
            break;
        }
        if (otherIndex === sortedIds.length)
          break;
        if (currentId === sortedIds[otherIndex]) {
          shownWorks.push(sortedTempWorks[index]);
          ++otherIndex;
        }
      }

      return shownWorks;
    }

    this.receivePapers = function(event, args) {
      /**
       * .. js.function:: receivePapers(event, args)
       *
       *    Fill the array with the given papers. Send a signal to the
       *    statistics if they a toggle was used.
       *
       *    :param event: ``triggerToggle`` or ``papers`` event.
       *    :param args: Dictionary containing name of the content
       *                 (i.e. ``papers``) and the information whether the
       *                 statistics should be recomputed.
       *    :returns: list of ids of the records.
       */
      this.$node.fnClearTable();
      this.contentType = args.name;

      var tempWorks = this[args.name];

      // Ids of papers that can be displayed.
      var ids = this.getIdsFromToggles();

      var sortedIds = ids.sort(function(a, b) {
        return a - b;
      });

      var shownWorks = [];

      if (args.name === 'externals') {

        // We don't have to do any unions, all papers are displayed.
        // Toggle filtering doesn't aplly to external papers.
        shownWorks = tempWorks;

      } else {

        var sortedTempWorks = tempWorks.sort(function(a, b) {
          // Note that there are only two possible situations.
          // All the papers have ids or
          // none of them (if args.name === 'external')
          if (a.hasOwnProperty('id') && b.hasOwnProperty('id'))
            return a.id - b.id;
          else
            return 0;
        });

        // Get the union of both arrays
        shownWorks = this.unionIds(sortedIds, sortedTempWorks);
      }

      this.sendAllWorks(event, sortedIds);

      if (shownWorks.length !== 0)
        this.$node.fnAddData(shownWorks);

    };

    this.toggle_counter = 0;

    this.fromToggle = function(event, args) {
      /**
       * .. js.function:: fromToggle(event, args)
       *
       *    Handle the change of a toggle.
       *
       *    :param event: ``triggerToggle`` event.
       *    :param args: dictionary containing the name of the toggle
       *
       *    :returns: List of ids of the records.
       */
      event.stopPropagation();

      this[args.name] = args.value;
      if (args.name == 'selfcited-checkbox')
        self_cited = args.value;

      if (this.toggle_counter < $('#toggles-list > li').length - 1) {
        // First events need to be supressed, as we don't have complete
        // information about toggles state.
        ++this.toggle_counter;
        return;
      }

      this.receivePapers(event, {
        name: this.contentType,
        recomputeStats: true
      })

    };

    this.getToggles = function() {
      /**
       * .. js.function:: getToggles()
       *
       *    Get values from the toggles.
       *
       *    :returns: dictionary with every key representing different toggle.
       */
      return {
        'collaboration-checkbox': this['collaboration-checkbox'],
        'arxiv-checkbox': this['arxiv-checkbox'],
        'singleauthored-checkbox': this['singleauthored-checkbox'],
        'selfcited-checkbox': this['selfcited-checkbox']
      };
    }

    this.sendAllWorks = function(event, sortedIds) {
      /**
       * .. js.function:: sendAllWorks(event, sortedIds)
       *
       *    :param event: ``triggerToggle`` event.
       *    :param args: dictionary (oprional) containing sorted ids of papers
       *                 to be shown and the information if a recomputation is
       *                 needed.
       *
       *    :returns: dictionary with every key representing different toggle.
       */

      var ranges = this.computeRanges();
      var ids = sortedIds;

      var tempWorks = $.extend(true, [], this.internalPapers).sort(function(a, b) {
        // External papers are out, so ids will be included.
        return a.id - b.id;
      });
      var statWorks = this.unionIds(ids, tempWorks);

      this.trigger('toggleChanged', {
        works: statWorks,
        toggles: this.getToggles(),
        ranges: ranges
      });
    };

    this.after('initialize', function() {

      var allPapers = JSON.parse($('#bootstrapped').html());
      this.papers = [];
      this.datasets = [];
      this.externals = [];
      
      // Fill the categories
      for (var i = allPapers.length - 1; i >= 0; i--) {
        var thi = allPapers[i];
        if (thi.type === 'Paper') {
          this.papers[this.papers.length] = thi;
        } else if (thi.type === "Data") {
          this.datasets[this.datasets.length] = thi;
        } else if (thi.type === "External") {
          this.externals[this.externals.length] = thi;
        }
      }

      // External papers are not used by the stats and thus should be removed.
      this.internalPapers = $.grep(allPapers, function(element, index) {
        return element.type !== "External";
      });

      // Listen to button for toggling which type of works should be shown.
      this.on(document, 'papers', this.receivePapers);

      // Listen to toggles for restricting data visibility.
      this.on(document, 'triggerToggle', this.fromToggle);

      // Create the main table.
      var tick = "<div class='fa fa-check text-success'></div>";
      try {
        var dataTable = this.$node.dataTable({
          "aaData": this.papers,
          "aoColumns": [

            // Represents the claimed tick
            {
              "sTitle": tick,
              "mData": "claimed",
              "sWidth": "10%",
              "mRender": function(data, type, full) {
                // Display tick when the paper is claimed.
                return data ? tick : ''
              },
              "sClass": "min-tablet"
            },

            // Title of the work
            {
              "sTitle": "Title",
              "mData": "title",
              "sWidth": "70%",
              "mRender": function(data, type, full) {
                var printed = data;
                // TO DO: more responsiveness
                if (printed.length > 70)
                  printed = printed.slice(0, 65) + "..."
                return '<a href="' + full.url + '">' + printed + '</a>';
              }
            },

            // When the work was written
            {
              "sTitle": "Year",
              "mData": "year",
              "sWidth": "10%"
            },

            // How many times the paper was cited
            {
              "sTitle": "Citations",
              "mData": "cited",
              "sWidth": "10%",
              "mRender": function(data, type, full) {
                if (self_cited)
                  return data ? data.length : '';
                else
                  return data ? $.grep(data, function(element, index) {
                    return !element.selfcitation
                  }).length : '';
              }
            },
          ],
          "bDeferRender": true,
          "bLengthChange": false,
          "iDisplayLength": 20,
          "responsive": true,
          "sDom": '<"top">rt<"pull-right"p>i',
          "sPaginationType": "bs_full"
        });

        // Turn on filtering capabilities
        $("#dataTables-filter").keyup(function() {
          dataTable.fnFilter(this.value);
        });
      } catch(err) {
        console.warn("WARNING: datatables failed: " + err.message);
      }

      // After the component is ready, ask toggles if they are enabled.
      this.trigger('askForToggles');

    });
  });

  return pubsList;

});
