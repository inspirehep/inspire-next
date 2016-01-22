/*
 * This file is part of INSPIRE.
 * Copyright (C) 2013, 2014, 2015, 2016 CERN.
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

    return defineComponent(HepApprovalAction);

    /**
     * .. js:class:: HepApprovalAction()
     *
     * Handles the events from the UI button elements for acceping/rejecting
     * records by sending the selected action to the server.
     *
     * :param string actionResolveSelector: DOM selector of elements resolving actions.
     * :param string action_url: URL for resolving the action.
     *
     */
    function HepApprovalAction() {

      this.attributes({
        actionAcceptSelector: ".hep-approval-action-accept",
        actionRejectSelector: ".hep-approval-action-reject",
        action_url: "",
        pdfCheckboxSelector: "[name='submission-data-pdf']"
      });


      // PDF-related functions
      this.get_pdf_submission_value = function() {
        return $(this.attr.pdfCheckboxSelector).prop("checked");
      };

      this.pdf_submission_readonly = function() {
        $(this.attr.pdfCheckboxSelector).prop("disabled", true);
      };


      // POST object init
      this.get_action_values = function(elem) {
        var actionValues = {
          "value": elem.data("value"),
          "objectids": []
        };

        actionValues.objectids.push(elem.data("objectid"));
        return actionValues;
      };


      // Action functions (batch + standard)
      this.onBatchAction = function(ev, data) {
        var payload = {
          "value": data.value,
          "objectids": data.selectedIDs
        };

        this.requestToServer(payload);
      };

      this.onAction = function(ev, data) {
        var element = $(data.el);
        var payload = this.get_action_values(element);

        payload.pdf_submission = this.get_pdf_submission_value();
        this.requestToServer(payload, element);
      };


      // Request to sever
      this.requestToServer = function(payload, element) {
        var $this = this;
        var objectids = payload.objectids;

        if (objectids.length > 0) {
          jQuery.ajax({
            type: "POST",
            url: $this.attr.action_url,
            data: payload,
            success: function(data) {
              $this.post_request(data);
              $this.trigger(document, "removeSentElements", {
                "ids": objectids
              });
            },
            error: function(request, status, error) {
              console.log(error);
            }
          });

          this.pdf_submission_readonly();
        }
      };

      this.post_request = function(data) {
        this.trigger(document, "updateAlertMessage", {
          category: data.category,
          message: data.message
        });

        // Check if we are in the details page or
        // the main list, to trigger the right event
        if (document.URL.indexOf('/details/')) {
          this.trigger(document, "changePage");
        } else {
          this.trigger(document, "reloadHoldingPenTable");
        }
      };


      this.after('initialize', function() {
        // Custom handlers for buttons
        this.on("click", {
          actionAcceptSelector: this.onAction,
          actionRejectSelector: this.onAction
        });
        // Batch action handler
        this.on(document, "return_data_for_exec", this.onBatchAction);

        if ($(this.attr.pdfCheckboxSelector).prop('disabled')) {
          this.pdf_submission_readonly();
        }
        console.log("HEP approval init");
      });
    }
  }
);
