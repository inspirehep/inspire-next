/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014 CERN.
 *
 * INSPIRE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */


define(function(require, exports, module) {
  "use strict";

  var $ = require("jquery");
  var tpl_flash_message = require('hgn!js/deposit/templates/flash_message');
  var DataMapper = require("js/deposit/mapper");
  var TaskManager = require("js/deposit/task_manager");
  var conferencesTypeahead = require("js/deposit/conferences_typeahead");
  var AffiliationsTypeahead = require("js/deposit/affiliations_typeahead");
  var PreviewModal = require("js/deposit/modal_preview");
  var SynchronizedField = require("js/deposit/synchronized_field");
  require("js/deposit/message_box");
  require("js/deposit/fields_group");
  require('ui/effect-highlight');
  require('ui/effect-blind');
  require("bootstrap-multiselect");
  require("bootstrap");
  require('js/deposit/dynamic_field_list');


  function HEPNamesSubmissionForm(options) {

    this.options = options;
    this.save_url = options.save_url;

    this.$submissionForm = $('#submitForm');
    this.$form = $("#webdeposit_form_accordion");
    this.$formWrapper = $('.form-wrapper');
    this.$inputs = this.$formWrapper.find(':input');

    this.init();
  }

  HEPNamesSubmissionForm.prototype = {

    /*
     * here proper initialization
     */
    init: function init() {

      var that = this;

      // focus on the first element of the form
      $('form:first *:input[type!=hidden]:first').focus();

      // subject field supports multiple selections
      // using the library bootstrap-multiselect
      $('#research_field').attr('multiple', 'multiple').multiselect({
        maxHeight: 400,
        enableCaseInsensitiveFiltering: true
      });
    }
  };

  /**
   * Clears the form data.  Takes the following actions on the form's input fields:
   *  - input text fields will have their 'value' property set to the empty string
   *  - input hidden fields will have their 'value' property set to the empty string
   *  - select elements will have their 'selectedIndex' property set to -1
   *  - checkbox and radio inputs will have their 'checked' property set to false
   *  - inputs of type submit, button, reset will *not* be effected
   *  - button elements will *not* be effected
   */
  $.fn.clearForm = function() {
    return this.each(function() {
      var type = this.type,
        tag = this.tagName.toLowerCase();
      if (tag === 'form') {
        return $(':input', this).clearForm();
      }
      if (type === 'text' || type === 'password' || type === 'hidden' || tag === 'textarea') {
        // avoid to clear the authors fields since they are already recreated
        if ($(this).parents('#field-authors').length === 0) {
          this.value = '';
        }
      } else if (type === 'checkbox' || type === 'radio') {
        this.checked = false;
      } else if (type === 'select-multiple') { // for the multi-select field
        if (this.selectedIndex !== -1) {
          $('#subject option').each(function() {
            $(this).prop('selected', false);
          });
          $('#subject').multiselect('refresh');
        }
      }
    });
  };

  /**
   * Resets the color of the imported fields
   */
  $.fn.resetColor = function() {
    return this.each(function() {
      var type = this.type,
        tag = this.tagName.toLowerCase();
      if (tag === 'form') {
        return $(':input', this).resetColor();
      }
      if (type === 'text' || tag === 'textarea') {
        if (this.id !== 'nonpublic_note') {
          $(this).css('background-color', '#fff');
        }
      }
    });
  };

  module.exports = HEPNamesSubmissionForm;
});
