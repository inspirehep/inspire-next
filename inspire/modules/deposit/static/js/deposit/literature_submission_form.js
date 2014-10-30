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
  var ConferencesTypeahead = require("js/deposit/conferences_typeahead");
  var PreviewModal = require("js/deposit/modal_preview");
  require("js/deposit/message_box");
  require("js/deposit/fields_group");
  require('ui/effect-highlight');
  require('ui/effect-blind');
  require("bootstrap-multiselect");
  require("bootstrap");
  require('js/deposit/dynamic_field_list');


  /**
   * This mapper assumes it receives standarized data format
   * after treating with another mapper.
   *
   * @type {DataMapper}
   */
  var literatureFormPriorityMapper = new DataMapper({

    common_mapping: function(data) {

      var priorities = {
        title: ['doi', 'arxiv'],
        title_arXiv: ['arxiv'],
        journal_title: ['doi', 'arxiv'],
        isbn: ['doi', 'arxiv'],
        page_range: ['doi', 'arxiv'],
        volume: ['doi', 'arxiv'],
        year: ['doi', 'arxiv'],
        issue: ['doi', 'arxiv'],
        authors: ['doi', 'arxiv'],
        abstract: ['doi', 'arxiv'],
        article_id: ['doi', 'arxiv'],
        license_url: ['arxiv'],
        note: ['arxiv'],
        page_nr: ['doi', 'arxiv']
      };

      var result = {};

      for (var field in priorities) {
        for (var idx in priorities[field]) {
          var source = priorities[field][idx];
          if (data[source] && data[source][field]) {
            result[field] = data[source][field];
            break;
          }
        }
      }
      return result;
    }
  });

  function LiteratureSubmissionForm(save_url) {

    this.save_url = save_url;

    // here just global form variables initialization
    this.$field_list = {
      article: $('*[class~="article-related"]'),
      thesis: $('*[class~="thesis-related"]'),
      chapter: $('*[class~="chapter-related"]'),
      book: $('*[class~="book-related"]'),
      proceedings: $('*[class~="proceedings-related"]'),
      translated_title: $("#state-group-title_translation"),
    };

    this.$doi_field = $("#doi");
    this.$arxiv_id_field = $("#arxiv_id");
    this.$isbn_field = $("#isbn");

    this.$deposition_type = $("#type_of_doc");
    this.$deposition_type_panel = this.$deposition_type.parents('.panel-body');
    this.$language = $("#language");
    this.$translated_title = $("#state-group-title_translation");
    this.$importButton = $("#importData");
    this.$skipButton = $("#skipImportData");
    this.$submissionForm = $('#submitForm');
    this.$conference = $('#conf_name');
    this.$conferenceId = $('#conference_id');
    this.$previewModal = $('#modalData');
    this.$nonpublic_note = $("#nonpublic_note");
    this.$form = $("#webdeposit_form_accordion");
    this.$formWrapper = $('.form-wrapper');
    this.$inputs = this.$formWrapper.find(':input');

    // these fields' values will be deleted before submission so that they will not be
    // sent to the sever
    this.$fieldsExcludedFromSubmision = [
      this.$conference
    ];

    this.$importIdsFields = $('form:first .panel:eq(0) *:input[type=text]');

    this.init();
    this.connectEvents();
  }

  LiteratureSubmissionForm.prototype = {

    /*
     * here proper initialization
     */
    init: function init() {

      var that = this;

      this.preventFormSubmit();

      // focus on the first element of the form
      $('form:first *:input[type!=hidden]:first').focus();

      this.slideUpFields(this.$field_list);

      this.fieldsGroup = $("#journal_title, #volume, #issue, #page_range, #article_id, #year")
        .fieldsGroup({
          onEmpty: function enableProceedingsBox() {
            that.$nonpublic_note.removeAttr('disabled');
            $('.tooltip-wrapper').tooltip('destroy'); // destroy the tooltip
          },
          onNotEmpty: function disableProceedingsBox() {
            that.$nonpublic_note.attr('disabled', 'true');
            $('.tooltip-wrapper').tooltip(); // trigger the tooltip
          }
        });

      // subject field supports multiple selections
      // using the library bootstrap-multiselect
      $('#subject').attr('multiple', 'multiple').multiselect({
        maxHeight: 400,
        enableCaseInsensitiveFiltering: true
      });

      this.hideHiddenFields();
      this.handleTranslatedTitle();
      this.taskmanager = new TaskManager(this.$deposition_type);
      // flash messages on the Modal
      this.messageBoxModal = $('#flash-import').messageBox({
        hoganTemplate: tpl_flash_message,
      })[0];
      // flash messages on the Form
      this.messageBoxForm = $('#flash-message').messageBox({
        hoganTemplate: tpl_flash_message,
      })[0];

      this.$conference.conferencesTypeahead({
        suggestionTemplate: Hogan.compile(
          '<b>{{ title }}</b><br>' +
          '<small>' +
          '{{ date }}, {{ place }}<br>' +
          '{{ conference_id }}' +
          '</small>'
        ),

        selectedValueTemplate: Hogan.compile(
          '{{ conference_id }}, {{ title }}, {{ date }}, {{ place }}'
        ),

        cannotFindMessage: 'Cannot find this conference in our database.'
      });

      this.previewModal = new PreviewModal(this.$previewModal, {
        labels: this.getLabels(),
        ignoredFields: this.getHiddenFields()
      });
    },

    /*
     * here binding functions to events
     */
    connectEvents: function connectEvents() {

      var that = this;

      this.$deposition_type.change(function(event) {
        that.onDepositionTypeChanged();
      });

      this.$language.change(function(event) {
        that.handleTranslatedTitle();
      });

      this.$importButton.click(function(event) {
        that.$importButton.button('loading');
        that.validate(that.$importIdsFields)
        // trigger like this because importData returns a Deferred object
        // and importData needs to have set 'this' to the form object
        .then(that.importData.bind(that))
          .always(function() {
            that.$importButton.button('reset');
          });
      });

      this.$skipButton.click(function(event) {
        that.showForm();
      });

      this.$submissionForm.on('submit', function(event) {
        that.$conferenceId.val(ConferencesTypeahead.getRawValue());
        that.deleteIgnoredValues();
      });
    },

    /**
     * Disable form submit on ENTER
     */
    preventFormSubmit: function preventFormSubmit() {
      this.$submissionForm.find("input").bind("keyup keypress", function(e) {
        var code = e.keyCode || e.which;
        if (code === 13) {
          e.preventDefault();
          return false;
        }
      });
    },

    /**
     * Validate fields, and show the errors.
     *
     * @param $fields {jQuery object} validated fields
     * @returns {jQuery.Deferred} the object is resolved when validation passes
     *  and rejected on errors
     */
    validate: function($fields) {

      var that = this;

      var deferredValidation = new $.Deferred();

      $.ajax({
        cache: false,
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(getRequestData($fields)),
        dataType: 'json',
        type: 'POST',
        url: that.save_url,
      }).done(function(data) {
        var hasError = false;
        if (!data.messages) {
          deferredValidation.reject();
          return;
        }
        $.each(data.messages, function(fieldName, field) {
          if (field.state === 'error') {
            hasError = true;
            that.$submissionForm.trigger("handleFieldMessage", {
              name: fieldName,
              data: field,
            });
          }
        });
        if (hasError) {
          deferredValidation.reject();
          return;
        }
        deferredValidation.resolve();
      });

      return deferredValidation;

      function getRequestData($fields) {
        var requestData = {};
        $.each($fields, function(idx, field) {
          requestData[field.id] = $(field).val();
        });
        return requestData;
      }
    },

    /**
     * Show the rest of the form except for the first panel
     */
    showForm: function showForm() {

      // mandatory indicator for required fields
      var $mandatoryIndicator = $('#mandatory-indicator');
      // action bar
      var $actionBar = $('.action-bar');

      $mandatoryIndicator.show('blind'); // default duration 400
      this.$formWrapper.show('blind', 1000);
      $actionBar.show('blind', 1000);
    },

    /**
     * Deletes fields from $fieldsExcludedFromSubmision property,
     * usually done before submission
     */
    deleteIgnoredValues: function deleteIgnoredValues() {
      $.each(this.$fieldsExcludedFromSubmision, function(i, $field) {
        $field.val('');
      });
    },

    /**
     * Hide form-group container of hidden fields
     *
     */
    hideHiddenFields: function hideHiddenFields() {
      // "not" part excludes field list elements e.g. authors
      // FIXME: move hidden html template element of DynamiFieldList
      //   to a Hogan template to get rid of 'not' part
      $('input[type="hidden"]')
        .not('[id$="__last_index__"]')
        .parents('.form-group')
        .hide();
    },

    onDepositionTypeChanged: function onDepositionTypeChanged() {
      this.slideUpFields(this.$field_list);
      var deposition_type = this.$deposition_type.val();
      var $type_related_fields = this.$field_list[deposition_type];
      var $type_related_groups = $type_related_fields.parents('.form-group');
      this.slideDownFields($type_related_groups);
      var $type_related_panel = $type_related_fields.parents('.panel-body');
      $type_related_panel.effect(
        "highlight", {
          color: "#e1efbb"
        },
        2500
      );
      this.$deposition_type_panel.children('.alert').remove('.alert');
      if (deposition_type === "proceedings") {
        this.$deposition_type_panel.append(tpl_flash_message({
          state: 'info',
          message: "<strong>Proceedings:</strong> only for complete " +
            "proceedings. For contributions use Article/Conference paper."
        }));
      }
    },

    importData: function importData() {

      var arxivSource = require("js/deposit/data_sources/arxiv");
      var doiSource = require("js/deposit/data_sources/doi");
      var isbnSource = require("js/deposit/data_sources/isbn");

      var arxivId = this.stripSourceTags(this.$arxiv_id_field.val());
      var doi = this.stripSourceTags(this.$doi_field.val());
      var isbn = this.$isbn_field.val();
      var depositionType = this.$deposition_type.val();

      var importTasks = [];

      var ImportTask = require("js/deposit/import_task");

      if (doi) {
        importTasks.push(new ImportTask(doiSource, doi, depositionType));
      }
      if (arxivId) {
        importTasks.push(new ImportTask(arxivSource, arxivId, depositionType));
      }
      if (isbn) {
        importTasks.push(new ImportTask(isbnSource, isbn, depositionType));
      }

      var that = this;

      return this.taskmanager.runMultipleTasksMerge(
        // tasks
        importTasks,
        // priority mapper for merging the results
        literatureFormPriorityMapper
      ).done(function(result) {
        that.messageBoxModal.clean();
        that.messageBoxForm.clean();

        // flash messages on the Form or Modal depending on the state of the message
        for (var i in result.statusMessage) {
          if (result.statusMessage[i].state === 'warning') {
            that.messageBoxForm.append(result.statusMessage);
          }
          if (result.statusMessage[i].state === 'success') {
            that.messageBoxModal.clean();
            that.messageBoxForm.clean();
            that.messageBoxModal.append(result.statusMessage);
          }
        }

        // clear the messages when user cancel to import data
        that.$previewModal.one("rejected", function(event) {
          that.messageBoxModal.clean();
          that.messageBoxForm.clean();
        });

        // only fill the form if the user accepts the data
        that.$previewModal.one("accepted", function(event) {
          that.$inputs.resetColor();
          that.$inputs.clearForm();
          that.fillForm(result.mapping);
          that.fieldsGroup.resetState();
          that.showForm();
        });

        // check if there are any data
        if (result.mapping) {
          that.previewModal.show(result.mapping);
        }
      });
    },

    /**
     * Returns ids of hidden elements
     */
    getHiddenFields: function getHiddenFields() {
      return $.map($('input.hidden'), function(value, index) {
        return value.id;
      });
    },

    /**
     * Returns object with keys named after the labels extracted from the form
     */
    getLabels: function getLabels() {
      var newObject = {};
      var $rows = $("div[id^='state-group-']");
      $.map($rows, function(row, index) {
        var $label = $(row).find('label');
        var label = $.trim($label.text());
        var $field = $label.attr('for');
        if ($label && label) {
          newObject[$field] = label;
        }
      });
      return newObject;
    },

    /**
     * Hide form fields individually related to each document type
     */
    slideUpFields: function slideUpFields($fields) {
      $.map($fields, function($field, field_name) {
        if (that.deposition_type != field_name) {
          $.each($field, function(i, f){
              $(f).parents('.form-group').slideUp();
          });
        }
      });
    },

    /**
     * Show form fields individually related to each document type
     */
    slideDownFields: function slideDownFields($fields) {
        $fields.slideDown();
    },

    /**
     * Hide or show translated title field regarding selected language
     */
    handleTranslatedTitle: function handleTranslatedTitle() {
      var language_value = this.$language.val();

      if (language_value !== 'en') {
        this.$translated_title.slideDown();
      } else {
        this.$translated_title.slideUp();
      }
    },

    /**
     * Strips the prefix off the identifier.
     * @param identifier DOI/arXiv/ISBN id
     * @returns stripped identifier
     */
    stripSourceTags: function stripSourceTags(identifier) {
      identifier = $.trim(identifier);
      var doi_prefix = /^doi:/;
      var arxiv_prefix = /^ar[xX]iv:/;

      var strippedID = identifier.replace(doi_prefix, '');
      strippedID = strippedID.replace(arxiv_prefix, '');

      return strippedID;
    },

    /**
     * Fills the deposit form according to schema in dataMapping
     *
     * @param dataMapping {} dictionary with schema 'field_id: field_value', and
     *  special 'authors' key to extract them to authors field.
     */
    fillForm: function fillForm(dataMapping) {
      var that = this;

      if ($.isEmptyObject(dataMapping)) {
        return;
      }

      var authorsWidget = $('#submitForm .dynamic-field-list.authors')
        .dynamicFieldList()[0];

      $.map(dataMapping, function(value, field_id) {
        var $field = $('#' + field_id);
        if ($field) {
          // highlight the imported fields except for the authors with the Bootstrap's success alert box
          if (field_id !== 'authors') {
            $field.css('background-color', '#dff0d8');
          }
          var field_value = $field.val(value);
        }
      });

      // ensure there is a one empty field
      if (authorsWidget.get_next_index() === 0) {
        authorsWidget.append_element();
      }

      // recreation of authors fields
      if (authorsWidget.$element.children('.field-list-element').length > 1) {
        authorsWidget.$element.children('.field-list-element').not(':first').each(function() {
          var $this = $(this);
          $this.remove();
          authorsWidget.update_elements_indexes();
        });
      }

      for (var i in dataMapping.authors) {
        authorsWidget.update_element(dataMapping.authors[i], i);
        // highlight the authors fields with the Bootstrap's success alert box
        $('#authors-' + i + '-name').css('background-color', '#dff0d8');
        // next index is i+1 but there should stay one empty field
        if (parseInt(i) + 2 > authorsWidget.get_next_index()) {
          authorsWidget.append_element();
        }
      }

      // triggers the "dataFormSave" in order the empty fields can be saved as well
      that.$submissionForm.trigger("dataFormSave", {
        url: that.save_url,
        form_selector: that.$submissionForm
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

  module.exports = LiteratureSubmissionForm;
});
