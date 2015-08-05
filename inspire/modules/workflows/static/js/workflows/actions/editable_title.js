/*
 * This file is part of Invenio.
 * Copyright (C) 2015 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */


define(
  [
    'jquery',
    'flight/lib/component',
    'hgn!js/workflows/templates/editable_title'
  ],
  function(
    $,
    defineComponent,
    title_modal_tpl) {

    'use strict';

    return defineComponent(EditableTitle);

    function EditableTitle() {

      this.attributes({
        titleSelector: "#title-text",
        editButtonSelector: "#edit-title",

        // Modal Selectors
        modalSelector: "#edit-title-modal",
        saveChangesSelector: "#save-changes",
        newTitleSelector: "#new-title",

        edit_url: "",
        objectid: "",
        newTitle: ""
      });

      this.createPayloadForEdit = function() {
        return {
          "value": this.attr.newTitle,
          "objectid": this.attr.objectid
        }
      };

      this.makeEditable = function(ev) {
        // Inject modal from template
        $(this.attr.modalSelector).replaceWith(title_modal_tpl({
          title: $(this.attr.titleSelector).text().trim()
        }));

        var that = this;
        $(this.attr.modalSelector)
          .modal('show')

          // Save title
          .on('click', this.attr.saveChangesSelector, function(ev) {
            that.attr.newTitle = $(that.attr.newTitleSelector).val().trim();

            // Replace the title with the edited one
            $(that.attr.titleSelector).text(that.attr.newTitle);
            that.makePostRequest();
          });
      };

      this.makePostRequest = function(ev) {
        var payload = this.createPayloadForEdit();
        var that = this;

        $.ajax({
          type: "POST",
          url: that.attr.edit_url,
          data: payload,
          success: function(data) {
            that.trigger(document, "updateAlertMessage", {
              category: data.category,
              message: data.message
            });
          }
        });
      };

      this.after('initialize', function() {
        this.on(this.attr.editButtonSelector, 'click', this.makeEditable);
        console.log("Editable Title OK");
      });
    }
  }
);