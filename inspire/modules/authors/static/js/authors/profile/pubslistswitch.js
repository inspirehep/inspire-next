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

  $ = require('jquery');

  var pubsListSwitch = require('flight/lib/component')(function() {

    this.trigger_tab = function(event) {
      /**
       * .. js:function:: trigger_tab
       *
       *    Send a signal to inform the list of the publication that the type
       *    of the content to be shown has been changed.
       *
       *    :param event: ``On click`` event which triggered this method.
       */
      event.stopPropagation();
      if (!this.$node.hasClass('active')) {
        // The pressed one wasn't already selected.
        $('.pubs-list-switch>ul>li').removeClass('active');
        this.$node.addClass('active');

        // Notify the table with the papers that it should show
        // another list.
        this.trigger('papers', {
          name: this.$node.attr('id')
        });
      }
    };

    this.after('initialize', function() {
      this.on('click', this.trigger_tab);
    });

  });

  return pubsListSwitch;

});
