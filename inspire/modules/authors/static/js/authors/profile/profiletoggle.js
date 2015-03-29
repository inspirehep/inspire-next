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
  require('bootstrap-switch');
  require('js/translate');
  $._ = _;

  var profileToggle = require('flight/lib/component')(function() {
    // single toggle

    this.trigger_toggle = function(event, state) {
      this.trigger('triggerToggle', {name: this.$node[0].name,
                                     value: this.$node.bootstrapSwitch('state')});
    };

    this.after('initialize', function() {
      this.$node.bootstrapSwitch({
        onText: $._('On'),
        offText: $._('Off')
      });
      this.on('switchChange.bootstrapSwitch', this.trigger_toggle);        
      this.on(document, 'askForToggles', this.trigger_toggle);
    });


  });

  return profileToggle;

});
