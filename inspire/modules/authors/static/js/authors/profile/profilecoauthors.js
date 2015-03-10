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
  var tpl_coauthors = require('hgn!../templates/coauthors');

  var profileCoauthors = require('flight/lib/component')(function() {

    // The body of co-authors box

    this.trigger_toggle = function(event, args) {
      /**
       * .. js:function:: trigger_toggle(event, args)
       *
       *    Compute coauthors statistics and display them.
       *
       *    :param event: ``toggleChanged`` event
       *    :args: dictionary containing works
       */
      var coauthors = {};

      $.each(args.works, function(index, value) {
        $.each(value['co-authors'], function(index, coauthor) {
          if (coauthor.id in coauthors)
            ++(coauthors[coauthor.id].quantity);
          else
            coauthors[coauthor.id] = {
              name: coauthor.name,
              quantity: 1
            };
        });
      });

      var coauthorsArray = $.map(coauthors, function(value, key) {
        return {
          // TO DO - should work like on legacy
          profile_link: key,
          number_of_papers: value.quantity,
          // TO DO - should work like on legacy
          search_link: "",
          name: value.name
        };
      });

      coauthorsArray = coauthorsArray.sort(function(a, b) {
        var quantityDifference = b.number_of_papers - a.number_of_papers;
        if (quantityDifference !== 0)
          return quantityDifference;
        else
          return a.name.toUpperCase().localeCompare(b.name.toUpperCase());
      });

      this.$node.html(tpl_coauthors({
        top_co_authors: coauthorsArray
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

  return profileCoauthors;
});
