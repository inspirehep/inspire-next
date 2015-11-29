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
    'flight/lib/component',
  ],
  function(
    $,
    defineComponent) {

    return defineComponent(CoreApprovalModal);

    /**
     * .. js:class:: CoreApprovalModal()
     *
     * Handles the events from the UI button elements for acceping/rejecting
     * records by sending the selected action to the server.
     *
     */
    function CoreApprovalModal() {

      this.attributes({
        modalPrefixSelector: "#rejection-modal-",
        modalContentPrefixSelector: "#message-text-",
        modalButtonSelector: ".reject-action"
      });

      this.loadModal = function(ev, data) {
        var element = $(this.attr.modalPrefixSelector + data.objectids[0]);
        element.modal('show');
      };


      this.buttonPressed = function(ev, data) {
        var button = $(ev.target); // Button that triggered the modal
        var objectid = button.data('objectid');
        console.log("Button: " + objectid);
        var $text = $(this.attr.modalContentPrefixSelector + objectid);
        var payload = {
          text: $text.val(),
          objectids: []
        };
        payload.objectids.push(objectid);
        var $modal = $(this.attr.modalPrefixSelector + objectid);
        console.log($modal);
        $modal.modal('hide');
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        this.trigger("rejectConfirmed", payload);
      };

      this.after('initialize', function() {
        this.on(document, "loadRejectionModal", this.loadModal);
        this.on("click", {
          modalButtonSelector: this.buttonPressed
        });
        console.log("Core approval modal init");
      });
    }
  }
);
