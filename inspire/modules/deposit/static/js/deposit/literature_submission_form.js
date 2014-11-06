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
        categories_arXiv: ['arxiv'],
        journal_title: ['doi', 'arxiv'],
        isbn: ['doi', 'arxiv'],
        volume: ['doi', 'arxiv'],
        year: ['doi', 'arxiv'],
        issue: ['doi', 'arxiv'],
        authors: ['doi', 'arxiv'],
        abstract: ['doi', 'arxiv'],
        license_url: ['arxiv'],
        preprint_created: ['arxiv'],
        note: ['arxiv'],
        page_nr: ['doi', 'arxiv'],
        page_range_article_id: ['doi', 'arxiv']
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
    };

    this.$doi_field = $("#doi");
    this.$arxiv_id_field = $("#arxiv_id");
    this.$isbn_field = $("#isbn");

    this.$deposition_type = $("#type_of_doc");
    this.$deposition_type_panel = this.$deposition_type.parents('.panel-body');
    this.$language = $("#language");
    this.$subject = $("#subject");
    this.$translated_title = $("#state-group-title_translation");
    this.$subject_relevance = $("#state-group-subject_relevance");
    this.$importButton = $("#importData");
    this.$skipButton = $("#skipImportData");
    this.$submissionForm = $('#submitForm');
    this.$conference = $('#conf_name');
    this.$conferenceId = $('#conference_id');
    this.$conferenceValidatorField = $('#state-conf_name');
    this.$previewModal = $('#modalData');
    this.$nonpublic_note = $("#nonpublic_note");
    this.$form = $("#webdeposit_form_accordion");
    this.$formWrapper = $('.form-wrapper');
    this.$inputs = this.$formWrapper.find(':input');

    /**
     * Dict with custom setter functions - a workaround for twitter typeahead
     * @type {{fieldId: function }}
     */
    this.setters = {};

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

      this.fieldsGroup = $("#journal_title, #volume, #issue, #page_range_article_id, #year")
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
      this.handleSubjectRelevance();
      this.taskmanager = new TaskManager(this.$deposition_type);
      // flash messages on the Form
      this.messageBox = $('#flash-message').messageBox({
        hoganTemplate: tpl_flash_message,
      })[0];

      conferencesTypeahead(this.$conference);

      this.previewModal = new PreviewModal(this.$previewModal, {
        labels: this.getLabels(),
        ignoredFields: this.getHiddenFields()
      });

      this.setSettersForTypeaheadFields();

      this.$conferenceId.synchronizedField({
        $frontendField: this.$conference,
        synchronizationEvents: 'typeahead:selected change blur',
        propagatedEvents: 'typeahead:selected change blur',
        synchronizationFn: function($originalField, $frontendField) {
          $originalField.val(
            $frontendField.data('extended-typeahead').getRawValue());
          $originalField.trigger('change');
        },
        reverseSynchronizationFn: function($originalField, $frontendField) {
          $frontendField.data('extended-typeahead')
            .initFromRawValue($originalField.val(), 0);
        },
      });

      this.addConferenceInfoField();
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

      this.$subject.change(function(event) {
        that.handleSubjectRelevance();
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

      this.$submissionForm.on("form:init-autocomplete", function(ev, data) {
        if (data.item.id.indexOf("affiliation") != -1) {
          $(data.item).affiliationsTypeahead();
        }
      }.bind(this));

      // for spinner at conferences typeahead
      this.$conference.on('typeahead:asyncrequest', function() {
        $(this).addClass('ui-autocomplete-loading');
      });
      this.$conference.on('typeahead:asynccancel typeahead:asyncreceive',
        function() {
          $(this).removeClass('ui-autocomplete-loading');
        }
      );

      // reminder about using the typeahead to get the conference.
      this.$conference.on('change blur typeahead:selected', function() {
        if (!this.$conferenceId.val() && $.trim(this.$conference.val())) {
          this.$conferenceInfoField.show();
        } else {
          this.$conferenceInfoField.hide();
        }
      }.bind(this));
    },

    addConferenceInfoField: function() {
      var $clone = this.$conferenceValidatorField.clone();
      $clone
        .attr('id', 'conferences-message')
        .removeClass('alert-danger')
        .addClass('alert-warning')
        .html('Please use suggestions to select a conference from our ' +
          'database.');
      this.$conferenceValidatorField.after($clone);
      this.$conferenceInfoField = $clone;
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
     * Sets special setter functions for typeahead fields, workaround for
     * https://github.com/twitter/typeahead.js/issues/1015
     *
     * @returns {*}
     */
    setSettersForTypeaheadFields: function() {
      return $.each($('input'), function(index, field) {
        var $field = $(field);
        var typeahead = $field.data('ttTypeahead');
        if (typeahead !== undefined) {
          this.setters[field.id] = function(value) {
            $field.typeahead('val', value);
          }
        }
      }.bind(this));
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

      // run checkDepositionType() only when showing the rest of the form
      this.checkDepositionType();
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
      this.checkDepositionType();
      this.deposition_type = this.$deposition_type.val();
      var $type_related_fields = this.$field_list[this.deposition_type];
      var $type_related_groups = $type_related_fields.parents('.form-group');
      var $type_related_panel = $type_related_fields.parents('.panel-body');
      $type_related_panel.effect(
        "highlight", {
          color: "#e1efbb"
        },
        2500
      );
      this.$deposition_type_panel.children('.alert').remove('.alert');
      if (this.deposition_type === "proceedings") {
        this.$deposition_type_panel.append(tpl_flash_message({
          state: 'info',
          message: "<strong>Proceedings:</strong> only for complete " +
            "proceedings. For contributions use Article/Conference paper."
        }));
      }
    },

    /**
     * Checks the deposition type and slideUp/slideDown the fields and panels
     * depending on it
     */
    checkDepositionType: function checkDepositionType() {
      var that = this;
      this.deposition_type = this.$deposition_type.val();

      var $not_type_related_fields = {};
      var $type_related_fields = {};
      for (var name in this.$field_list) {
        if (name !== this.deposition_type && this.$field_list.hasOwnProperty(name)) {
          $not_type_related_fields[name] = this.$field_list[name];
        }
        if (name === this.deposition_type && this.$field_list.hasOwnProperty(name)) {
          $type_related_fields[name] = this.$field_list[name];
        }
      }

      // Slide Up
      $.when.apply(this, $.map($not_type_related_fields, function(value, key) {
        return that.slideUpFields(value.not('.hidden'));
      })).done(function() {
        that.slideUpPanel();
      });

      // Slide Down
      $.when.apply(this, $.map($type_related_fields, function(value, key) {
        return that.slideDownFields(value.not('.hidden'));
      })).done(function() {
        that.slideDownPanel();
      });
    },

    /**
     * Slide Up empty Panels
     */
    slideUpPanel: function slideUpPanel() {
      var $allPanels = $('.form-wrapper')
        .children('.panel:gt(0)');

      $.each($allPanels, function($field, field_name) {
        // all elements hidden
        if ($(field_name)
          .children('.panel-collapse')
          .children('.panel-body')
          .children('.form-group:visible')
          .length === 0) {
          $(field_name).slideUp();
        }
      });
    },

    /**
     * Slide Down empty Panels
     */
    slideDownPanel: function slideUpPanel() {
      var $allPanels = $('.form-wrapper')
        .children('.panel:gt(0)');

      $.each($allPanels, function($field, field_name) {
        // not all elements hidden
        if ($(field_name)
          .children('.panel-collapse')
          .children('.panel-body')
          .children('.form-group')
          .css('display') === 'block') {
          $(field_name).slideDown();
        }
      });
    },

    /**
     * Hide form fields individually related to each document type
     */
    slideUpFields: function slideUpFields($fields) {
      var deferred = $.map($fields, function(field_name, $field) {
        return $(field_name).parents('.form-group').slideUp().promise();
      });
      return $.when.apply(this, deferred);
    },

    /**
     * Show form fields individually related to each document type
     */
    slideDownFields: function slideDownFields($fields) {
      var deferred = $.map($fields, function(field_name, $field) {
        return $(field_name).parents('.form-group').slideDown().promise();
      });
      return $.when.apply(this, deferred);
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
        that.messageBox.clean();
        // check if there are any data
        if (result.mapping) {
          // only fill the form if the user accepts the data
          that.$previewModal.one("accepted", function(event) {
            that.$inputs.resetColor();
            that.$inputs.clearForm();
            that.fillForm(result.mapping);
            that.fieldsGroup.resetState();
            that.showForm();
          });
          // show the modal with result
          that.previewModal.show(result);
        } else { // show the error messages
          that.messageBox.append(result.statusMessages);
        }
      });
    },

    /**
     * Returns ids of hidden elements
     */
    getHiddenFields: function getHiddenFields() {
      // FIXME: it does not include fields different than ones of input type
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
     * Hide or show relevance to subject box depending on selected subject
     */
    handleSubjectRelevance: function handleSubjectRelevance() {
      var subjects = this.$subject.val();
      if (subjects === null) subjects = [];
      var HEP_subjects = $.grep(subjects, function(element) {
        return element.indexOf("HEP") > -1
      });
      if (typeof HEP_subjects === "undefined" || HEP_subjects.length === 0) {
        this.$subject_relevance.slideDown();
      }
      else {
        this.$subject_relevance.slideUp();
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
          var setter = this.setters[$field.attr('id')];
          // FIXME: workaround for
          // https://github.com/twitter/typeahead.js/issues/1015
          if (setter) {
            setter(value);
          } else {
            $field.val(value);
          }
        }
      }.bind(this));

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
