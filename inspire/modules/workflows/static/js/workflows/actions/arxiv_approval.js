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

    return defineComponent(ArxivApprovalAction);

    /**
    * .. js:class:: ArxivApprovalAction()
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
    function ArxivApprovalAction() {

      this.attributes({
        actionAcceptSelector: ".arxiv-approval-action-accept",
        actionRejectSelector: ".arxiv-approval-action-reject",
        actionGroupSelector: ".arxiv-approval-action",
        action_url: "",
        pdfCheckboxSelector: "[name='submission-data-pdf']"
      });

      this.get_action_values = function (elem) {
        return {
          "value": elem.data("value"),
          "objectid": elem.data("objectid")
        };
      };

      this.doBatchAction = function(ev, data) {
        if (data.command == "reject") {
          //this.doRejection(ev, data);
        } else {
          //this.onAccept(ev, data);
        }
        console.log(data.command);
        for (var i = 0; i < data.selectedIDs.length; i++)
          console.log(data.selectedIDs[i]);
      };

      this.get_pdf_submission_value = function () {
        return $(this.attr.pdfCheckboxSelector).prop("checked");
      };

      this.post_request = function(data, element) {
        console.log(data.message);
        this.trigger(document, "updateAlertMessage", {
          category: data.category,
          message: data.message
        });
        var parent = element.parents(this.attr.actionGroupSelector);
        if (typeof parent !== 'undefined') {
          parent.fadeOut();
        }
        this.trigger(document, "reloadHoldingPenTable");
        // FIXME: on the details page we should move to next record instead
      };

      this.onAccept = function (ev, data) {
        var element = $(data.el);
        var payload = this.get_action_values(element);
        var pdf_submission = this.get_pdf_submission_value();
        if (pdf_submission) {
          payload.pdf_submission = pdf_submission;
        }

        var $this = this;

        jQuery.ajax({
          type: "POST",
          url: $this.attr.action_url,
          data: payload,
          success: function(data) {
            $this.post_request(data, element);
          }
        });
        this.pdf_submission_readonly();
      };

      this.doRejection = function (ev, data) {
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
        this.pdf_submission_readonly();
      };

      this.pdf_submission_readonly = function () {
        $(this.attr.pdfCheckboxSelector).prop("disabled", true);
      };

      this.after('initialize', function() {
        // Custom handlers
        this.on("click", {
          actionAcceptSelector: this.onAccept,
          actionRejectSelector: this.doRejection
        });

        this.on(document, "return_data_for_exec", this.doBatchAction);

        if ($(this.attr.pdfCheckboxSelector).prop('disabled')) {
          this.pdf_submission_readonly();
        }
        console.log("Arxiv approval init");
      });
    }
  }
);
