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

'use strict';

define(
  [
    'jquery',
    'flight/component',
  ],
  function(
    $,
    defineComponent) {

    return defineComponent(CoreApprovalAction);

    /**
    * .. js:class:: CoreApprovalAction()
    *
    * Handles the events from the UI button elements for acceping/rejecting
    * records by sending the selected action to the server.
    *
    * The actionGroupSelector is required for handling display of any action
    * elements to be hidden or shown. It should be wrapped around every action
    * UI component.
    *
    * :param string actionResolveSelector: DOM selector of elements resolving actions.
    * :param string actionGroupSelector: DOM selector for wrapping display elements
    * :param string action_url: URL for resolving the action.
    *
    */
    function CoreApprovalAction() {

      this.attributes({
        actionResolveSelector: ".core-approval-action-resolve",
        actionGroupSelector: ".core-approval-action",
        action_url: ""
      });

      this.get_action_values = function (elem) {
        return {
          "value": elem.data("value"),
          "objectid": elem.data("objectid"),
        }
      };

      this.post_request = function(data, element) {
        console.log(data.message);
        console.log("This is CORE!");
        var parent = element.parents(this.attr.actionGroupSelector);
        if (typeof parent !== 'undefined') {
          parent.fadeOut();
        }
        //$(document).trigger("");
      };

      this.onActionClick = function (ev, data) {
        var element = $(data.el);
        var payload = this.get_action_values(element);
        var $this = this;

        jQuery.ajax({
          type: "POST",
          url: $this.attr.action_url,
          data: payload,
          success: function(data) {
            $this.post_request(data, element);
          }
        });
      };

      this.after('initialize', function() {
        // Custom handlers
        this.on("click", {
          actionResolveSelector: this.onActionClick
        });
        console.log("Core approval init");
      });
    }
  }
);
