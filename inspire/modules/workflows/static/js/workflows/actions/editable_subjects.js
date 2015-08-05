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
        editButtonSelector: "#edit-subjects",
        tagsContainerSelector: "#tags-container",
        saveChangesSelector: "#save-changes",

        edit_url: "",
        objectid: "",
        subjText: "",
        splitter: "Subject: ",

        knowledgeBaseUrl: "/api/knowledge/Subjects/mappings",

        tagInput: {},
        shortcodes: []
      });

      this.createPayloadForEdit = function() {
        return {
          "objectid": this.attr.objectid,
          "subjects": this.attr.tagInput.tagsinput('items').map(function(x) {return x.trim();})
        };
      };


      // Init Tags with proper events
      this.initTagInput = function() {
        var that = this;
        this.attr.tagInput = $("input#edit-subj:text");


        // Differentiate the colors between the existing and the new tags
        this.attr.tagInput.tagsinput({
          tagClass: function (item) {
            var subjectCodes = that.attr.shortcodes
              .map(function(shortcode) { return shortcode.to; });

            var subject = $.trim(item);

            if ($.inArray(subject, subjectCodes) !== -1) return 'label label-success';
            else return 'label label-info';
          }
        });


        // Add the existing subjects, and focus inside the input box
        this.attr.tagInput.tagsinput('add', this.attr.subjText);
        this.attr.tagInput.tagsinput('focus');


        // Filter the input and add the right one according to
        // the shortcodes. E.g. a -> Astrophysics
        this.attr.tagInput.on('beforeItemAdd', function(ev) {
          var originalValue = ev.item;
          var newValue = that.attr.shortcodes
            .filter(function(shortcode) { return shortcode.from === originalValue; })
            .map(function(shortcode) { return shortcode.to; })
            .toString();

          // Check if a new value was returned;
          // if not, add the original value to the tag
          ev.item = newValue ? newValue : originalValue;
        });
      };


      // Editable - Uneditable Input
      this.makeEditable = function(ev) {
        this.attr.subjText = $(this.attr.editSelector)
          .text()
          .split(this.attr.splitter)[1];

        // Replace the subjects div with the editable subjects input
        $(this.attr.editSelector).replaceWith(tpl_tags());

        this.initTagInput();
        this.on(this.attr.saveChangesSelector, 'click', this.makePostRequest);
      };

      this.makeUneditable = function() {
        // Replace the tags input with the non-editable subjects template
        $(this.attr.tagsContainerSelector).replaceWith(tpl_editable_subj({
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


      this.getSubjectShortcodes = function() {
        var that = this;
        $.ajax({
          type: "GET",
          dataType: "json",
          url: that.attr.knowledgeBaseUrl,
          success: function(data) {
            that.attr.shortcodes = data;
          }
        });
      };

      this.after('initialize', function() {
        this.on(this.attr.editButtonSelector, 'click', this.makeEditable);
        this.getSubjectShortcodes();

        console.log("Editable Subjects OK");
      });
    }
  }
);
