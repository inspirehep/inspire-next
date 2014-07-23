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
      contributors: ['doi', 'arxiv'],
      abstract: ['doi', 'arxiv'],
      article_id: ['doi', 'arxiv'],
      license_url: ['arxiv'],
      note: ['arxiv']
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

function LiteratureSubmissionForm() {

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

  this.init();
  this.connectEvents();
}

LiteratureSubmissionForm.prototype = {

  /*
   * here proper initialization
   */
  init: function init() {

    this.slideUpFields(this.$field_list);

    this.fieldsGroup = $("#journal_title, #volume, #issue, #page_range, #article_id, #year")
      .fieldsGroup({
        onEmpty: function enableProceedingsBox() {
          $("#nonpublic_note").removeAttr('disabled');
        },
        onNotEmpty: function disableProceedingsBox() {
          $("#nonpublic_note").attr('disabled', 'true');
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
    this.messageBox = $('#flash-import').messageBox({
      hoganTemplate: tpl_flash_message,
    })[0];
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
      that.importData();
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
    $type_related_groups.slideDown();
    var $type_related_panel = $type_related_fields.parents('.panel-body');
    $type_related_panel.effect(
      "highlight", {
        color: "#e1efbb"
      },
      2500
    );
    this.$deposition_type_panel.children('.alert').remove('.alert');
    if (deposition_type === "proceedings") {
      this.$deposition_type_panel.append(tpl_flash_message.render({
        state: 'info',
        message: "<strong>Proceedings:</strong> only for complete " +
          "proceedings. For contributions use Article/Conference paper."
      }));
    }
  },

  importData: function importData() {

    var arxivId = this.stripSourceTags(this.$arxiv_id_field.val());
    var doi = this.stripSourceTags(this.$doi_field.val());
    var isbn = this.$isbn_field.val();
    var depositionType = this.$deposition_type.val();

    var importTasks = [];

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

    this.taskmanager.runMultipleTasksMerge(
      // tasks
      importTasks,
      // priority mapper for merging the results
      literatureFormPriorityMapper,
      // callback
      function(result) {
        that.fillForm(result.mapping);
        that.fieldsGroup.resetState();
        that.messageBox.clean();
        that.messageBox.append(result.statusMessage);
        that.$importButton.button('reset');
      }
    );
  },

  /**
   * Hide form fields individually related to each document type
   */
  slideUpFields: function slideUpFields($fields) {
    $.map($fields, function($field, field_name) {
      $field.parents('.form-group').slideUp();
    });
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
   *  special 'contributors' key to extract them to authors field.
   */
  fillForm: function fillForm(dataMapping) {

    if ($.isEmptyObject(dataMapping)) {
      return;
    }

    var authorsWidget = DEPOSIT_FORM.field_lists.authors;

    $.map(dataMapping, function(value, field_id) {
      var $field = $('#' + field_id);
      if ($field) {
        $field.val(value);
        // Clean up pending messages on the field
        DEPOSIT_FORM.handle_field_msg(field_id, value);
      }
    });

    // ensure there is a one empty field
    if (authorsWidget.get_next_index() === 0) {
      authorsWidget.append_element();
    }

    for (var i in dataMapping.contributors) {
      authorsWidget.set_element_values(i, dataMapping.contributors[i]);
      // next index is i+1 but there should stay one empty field
      if (parseInt(i) + 2 > authorsWidget.get_next_index()) {
        authorsWidget.append_element();
      }
    }
  }
}
