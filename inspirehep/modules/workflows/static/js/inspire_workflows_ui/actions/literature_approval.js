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
    'js/inspire_workflows_ui/actions/approval'
  ],
  function(
    $,
    flight,
    ApprovalAction) {

    "use strict";

    return flight.component(LiteratureApprovalAction, ApprovalAction);

    /**
     * .. js:class:: LiteratureApprovalAction()
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
    function LiteratureApprovalAction() {

      this.attributes({
        actionAcceptSelector: ".literature-approval-action-accept",
        actionRejectSelector: ".literature-approval-action-reject",
        pdfCheckboxSelector: "[name='submission-data-pdf']",
        rejection_modal: true,
        api_url: function() {
            return $("#workflows-ui-init").data('api-url');
        },
      });

      this.after('initialize', function() {
        // On button clicks
        this.on("click", {
          actionAcceptSelector: this.onAccept,
          actionRejectSelector: this.onReject
        });
        // Post rejection modal handler
        this.on("rejectConfirmed", this.doRejection);
        // Batch action handler
        this.on(document, "return_data_for_exec", this.onBatchAction);

        if ($(this.attr.pdfCheckboxSelector).prop('disabled')) {
          this.pdf_submission_readonly();
        }
        console.log("Approval init");
      });
    }
  }
);
