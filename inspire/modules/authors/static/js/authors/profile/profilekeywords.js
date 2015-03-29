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

  require('readmore');
  var tpl_keywords = require('hgn!../templates/keywords');

  var profileKeywords = require('flight/lib/component')(function() {

    // The body of the keywords box

    this.trigger_toggle = function(event, args) {
      /**
       * .. js:function:: trigger_toggle(event, args)
       *
       *    Compute keywords statistics and display them.
       *
       *    :param event: ``toggleChanged`` event
       *    :args: dictionary containing works
       */
      var keywords = {};

      // Get dictionary (key, number of occurences)
      $.each(args.works, function(index, value) {
        $.each(value.keywords, function(jindex, keyword) {
          if (keyword in keywords)
            ++keywords[keyword];
          else
            keywords[keyword] = 1;
        });
      });

      var keywordsArray = $.map(keywords, function(value, key) {
        return [
          [value, key]
        ];
      });

      // Sort and show
      keywordsArray = keywordsArray.sort(function(a, b) {
        var firstIndex = b[0] - a[0];
        if (firstIndex !== 0)
          return firstIndex;
        else
          return a[1].toUpperCase().localeCompare(b[1].toUpperCase());
      });

      keywordsArray = $.map(keywordsArray, function(value, index) {
        return {
          name: value[1],
          // TO DO - should work like on legacy
          search_link: "",
          number_of_papers: value[0]
        };
      });

      this.$node.html(tpl_keywords({
        top_keywords: keywordsArray
      }));
      this.$node.readmore({
        lessLink: '<div><a href="#"><i class="fa fa-plus"></i> Less</a></div>',
        moreLink: '<div><a href="#"><i class="fa fa-plus"></i> More</a></div>'
      });
    };

    this.after('initialize', function() {
      this.on(document, 'toggleChanged', this.trigger_toggle);
    });
  });

  return profileKeywords;
});
