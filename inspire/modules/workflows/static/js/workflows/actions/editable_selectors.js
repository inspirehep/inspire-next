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
    'hgn!js/workflows/templates/alert_editable'
  ],
  function(
    $,
    defineComponent,
    tpl_alert_editable) {

    'use strict';

    return defineComponent(EditableSelectors);

    function EditableSelectors() {

      this.attributes({
        previousText: "",
        edit_url: "",
        objectid: "",

        // Selectors
        confirmUpdateSelector: "#confirm-update",
        titleSelector: ".editable"
      });


      // Get record information
      this.getEventField = function(ev) {
        return ev.target.getAttribute('field-value');
      };

      this.getEventInnerHTML = function(ev) {
        return ev.target.innerHTML;
      };

      this.createPayloadForEdit = function(ev) {
        return {
          "field": this.getEventField(ev),
          "value": this.getEventInnerHTML(ev),
          "objectid": this.attr.objectid
        }
      };


      this.becomeEditable = function(ev) {
        if(window.getSelection) {
          var sel = window.getSelection();
          sel.removeAllRanges();
        }

        this.attr.previousText = this.getEventInnerHTML(ev);

        console.log("Selected text: " + this.attr.previousText);

        $(".editable[field-value='"+ this.getEventField(ev) +"']")
          .addClass('active-editable')
          .attr('contenteditable','true')
          .focus();
      };

      this.makePostRequest = function(ev) {

        /*$(this.attr.confirmUpdateSelector).html(tpl_alert_editable({
          previousText: this.attr.previousText,
          newText: this.getEventInnerHTML(ev)
        }));*/

        var payload = this.createPayloadForEdit(ev);

        var that = this;
        $.ajax({
          type: "POST",
          url: that.attr.edit_url,
          data: payload,

          success: function() {
            $(".editable[field-value='"+ that.getEventField(ev) +"']")
              .attr('contenteditable','false')
              .removeClass('active-editable');
          },

          error: function(request, status, error) {
            console.log(error);
            console.log(status);

            $(".editable[field-value='"+ that.getEventField(ev) +"']")
              .attr('contenteditable','false')
              .removeClass('active-editable');
          }
        });

        this.attr.previousText = "";
        console.log('New text: ' + this.getEventInnerHTML(ev));
      };


      this.after('initialize', function() {
        this.on('dblclick', {
          titleSelector: this.becomeEditable
        });
        this.on('focusout', {
          titleSelector: this.makePostRequest
        });

        console.log("Editable selections init");
      });
    }
  }
);