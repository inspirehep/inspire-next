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

    return defineComponent(EditableSelectors);

    function EditableSelectors() {

      this.attributes({
        edit_url: "",
        objectid: "",

        // Selectors
        editableClassSelector: ".editable"
      });


      // Get record information
      this.getEventField = function(ev) {
        return ev.target.getAttribute('data-field');
      };

      this.getEventInnerHTML = function(ev) {
        return ev.target.innerHTML;
      };

      this.getEventSelector = function(ev) {
        return this.attr.editableClassSelector +
          "[data-field='"+ this.getEventField(ev) +"']";
      };

      this.createPayloadForEdit = function(ev) {
        return {
          "field": this.getEventField(ev),
          "value": this.getEventInnerHTML(ev),
          "objectid": this.attr.objectid
        }
      };

      this.makeElementEditable = function(ev) {
        $(this.getEventSelector(ev))
          .addClass('active-editable')
          .attr('contenteditable','true')
          .focus();
      };

      this.makeElementUnEditable = function(ev) {
        $(this.getEventSelector(ev))
          .attr('contenteditable','false')
          .removeClass('active-editable');
      };


      this.becomeEditable = function(ev) {
        if (!$(this.getEventSelector(ev)).hasClass("active-editable")) {
          if (window.getSelection) {
            var sel = window.getSelection();
            sel.removeAllRanges();
          }

          this.makeElementEditable(ev);
        }
      };

      this.makePostRequest = function(ev) {
        var payload = this.createPayloadForEdit(ev);

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

          error: function(request, status, error) {
            console.log(error);
            console.log(status);
          },

          complete: function() {
            that.makeElementUnEditable(ev)
          }
        });

        this.attr.previousText = "";
        console.log('New text: ' + this.getEventInnerHTML(ev));
      };


      this.after('initialize', function() {
        this.on('dblclick', {
          editableClassSelector: this.becomeEditable
        });
        this.on('focusout', {
          editableClassSelector: this.makePostRequest
        });

        console.log("Editable selections init");
      });
    }
  }
);