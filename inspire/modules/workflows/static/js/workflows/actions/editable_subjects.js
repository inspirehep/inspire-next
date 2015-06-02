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
    'bootstrap-tagsinput',
    'flight/lib/component',
    'hgn!js/workflows/templates/editable_subjects',
    'hgn!js/workflows/templates/editable_subjects_tags'
  ],
  function(
    $,
    tagsinput,
    defineComponent,
    tpl_editable_subj,
    tpl_tags) {

    'use strict';

    return defineComponent(EditableSubjects);

    function EditableSubjects() {

      this.attributes({
        editSelector: "#editable-subjects",
        tagsContainerSelector: "#tags-container",

        edit_url: "",
        objectid: "",
        subjText: "",
        splitter: "Subject: ",

        tagInput: {}
      });

      this.createPayloadForEdit = function() {
        return {
          "objectid": this.attr.objectid,
          "subjects": this.attr.tagInput.tagsinput('items').map(function(x) {return x.trim();})
        }
      };

      this.initTagInput = function() {
        this.attr.tagInput = $("input");
        this.attr.tagInput.tagsinput();
        this.attr.tagInput.tagsinput('add', this.attr.subjText);
        this.attr.tagInput.tagsinput('focus');

        this.on(this.attr.tagsContainerSelector, 'focusout', this.makePostRequest);
      };

      this.makeEditable = function(ev) {
        this.attr.subjText = $(this.attr.editSelector)
          .text()
          .split(this.attr.splitter)[1];

        // Add the tags container
        $(this.attr.editSelector).replaceWith(tpl_tags());
        this.initTagInput();
      };

      this.makeUneditable = function() {
        $(this.attr.tagsContainerSelector).html(tpl_editable_subj({
          subjects: this.attr.tagInput.val()
        }));
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
            that.makeUneditable();
            that.on(that.attr.editSelector, 'dblclick', that.makeEditable);
          }
        });
      };

      this.after('initialize', function() {
        this.on(this.attr.editSelector, 'dblclick', this.makeEditable);

        console.log("Editable Subjects OK");
      });
    }
  }
);