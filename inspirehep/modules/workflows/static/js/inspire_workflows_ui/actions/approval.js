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
    'flight',
  ],
  function(
    $,
    flight) {

    "use strict";

    return ApprovalAction;

    /**
     * .. js:class:: ApprovalAction()
     *
     * Handles the events from the UI button elements for acceping/rejecting
     * records by sending the selected action to the server.
     *
     * The actionGroupSelector is required for handling display of any action
     * elements to be hidden or shown. It should be wrapped around every action
     * UI component.
     *
     * :param string actionResolveSelector: DOM selector of elements resolving actions.
     * :param string api-url: URL for resolving the actions.
     *
     */
    function ApprovalAction() {

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

        this.batchRequestToServer(payload);
      };

      this.onAccept = function(ev, data) {
        var element = $(data.el);
        var payload = this.get_action_values(element);

        var pdf_submission = this.get_pdf_submission_value();
        if (pdf_submission) {
          payload.pdf_submission = pdf_submission;
        }

        this.requestToServer(payload, element);
      };

      this.onReject = function(ev, data) {
        var element = $(data.el);
        var payload = this.get_action_values(element);

        var pdf_submission = this.get_pdf_submission_value();
        if (pdf_submission) {
          payload.pdf_submission = pdf_submission;
        }

        if (this.attr.rejection_modal) {
            this.trigger(document, "loadRejectionModal", payload);
        } else {
            this.requestToServer(payload, element);
        }
      };

      this.doRejection = function(ev, data) {
        data.value = "reject";
        var element = $(this.attr.actionRejectSelector + "[data-objectid=" + data.objectid + "]");
        this.requestToServer(data, element);
      };

      // Request to sever
      this.requestToServer = function(payload, element) {
        var $this = this;

        $.ajax({
          type: "POST",
          url: this.get_action_url(payload.objectids[0]),
          data: payload,
          success: function(data) {
            $this.post_request(data, element);
          }
        });
        this.pdf_submission_readonly();
      };

      // Request to sever
      this.batchRequestToServer = function(payload, element) {
        var $this = this;
        var objectids = payload.objectids;

        if (objectids.length > 0) {
          $.ajax({
            type: "POST",
            url: this.get_batch_url(),
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

      this.get_batch_url = function() {
          return this.attr.api_url + "action/resolve";
      }

      this.get_action_url = function(objectid) {
          return this.attr.api_url + objectid + "/action/resolve";
      }

      this.post_request = function(data, element) {
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
    }
  }
);
