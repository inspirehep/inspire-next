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
    'flight/lib/component'
  ],
  function(
    $,
    defineComponent) {

    'use strict';

    return defineComponent(EditableTitle);

    function EditableTitle() {

      this.attributes({
        editSelector: "#editable-title",
        activeEditableClass: "active-editable",

        edit_url: "",
        objectid: ""
      });

      this.createPayloadForEdit = function() {
        return {
          "value": $(this.attr.editSelector).html(),
          "objectid": this.attr.objectid
        }
      };

      // Editable/Uneditable Elements
      this.makeEditable = function(ev) {
        if (!$(this.attr.editSelector).hasClass(this.attr.activeEditableClass) && window.getSelection) {
          var sel = window.getSelection();
          sel.removeAllRanges();
        }
        $(this.attr.editSelector)
          .addClass(this.attr.activeEditableClass)
          .attr('contenteditable', 'true')
          .focus();
      };

      this.makeUneditable = function() {
        $(this.attr.editSelector)
          .removeClass(this.attr.activeEditableClass)
          .attr('contenteditable','false');
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
          },
          complete: function() {
            that.makeUneditable()
          }
        });
      };

      this.after('initialize', function() {
        this.on(this.attr.editSelector, 'dblclick', this.makeEditable);
        this.on(this.attr.editSelector, 'focusout', this.makePostRequest);

        console.log("Editable Title OK");
      });
    }
  }
);