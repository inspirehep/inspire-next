/*
 * This file is part of INSPIRE.
 * Copyright (C) 2013, 2014 CERN.
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
    'flight/lib/component'
  ],
  function(
    $,
    defineComponent) {

    "use strict";

    return defineComponent(BatchActionHotkeys);

    function BatchActionHotkeys() {
      this.batchActions = function(event) {
        var keyCodes = {
          rKey: 82,
          aKey: 65,
          cKey: 67
        };

        // Hotkey events for batch actions
        // Alt + A: Accept All
        // Alt + C: Accept CORE
        // Alt + R: Reject All
        if (event.altKey && event.keyCode === keyCodes.aKey) {
          this.trigger(document, "execute", {
            "value": "accept"
          });
          event.preventDefault();
        }
        if (event.altKey && event.keyCode === keyCodes.cKey) {
          this.trigger(document, "execute", {
            "value": "accept_core"
          });
          event.preventDefault();
        }
        if (event.altKey && event.keyCode === keyCodes.rKey) {
          this.trigger(document, "execute", {
            "value": "reject"
          });
          event.preventDefault();
        }
      };

      this.after('initialize', function() {
        this.on(document, "keydown", this.batchActions);
        console.log("Batch Action Init");
      });
    }
  }
);
