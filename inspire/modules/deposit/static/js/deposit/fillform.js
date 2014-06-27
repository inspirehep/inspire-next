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

$(document).ready( function() {

  var $field_list = {
    article: $('*[class~="article-related"]'),
	  thesis: $('*[class~="thesis-related"]'),
	  chapter: $('*[class~="chapter-related"]'),
	  book: $('*[class~="book-related"]'),
	  proceedings: $('*[class~="proceedings-related"]'),
    translated_title: $("#state-group-title_translation"),
  };

  var $doi_field = $("#doi");
  var $arxiv_id_field = $("#arxiv_id");
  var $isbn_field = $("#isbn");

	/**
	 * Hide form fields individually related to each document type
	 */
	function hideFields(){
		$.map($field_list, function($field, field_name){
			$field.parents('.form-group').slideUp();
		});
	}

	hideFields();

	var $deposition_type = $("#type_of_doc");
  var $deposition_type_panel = $deposition_type.parents('.panel-body');

	$deposition_type.change(function(event) {
		hideFields();
    var deposition_type = $deposition_type.val();
    var $type_related_fields = $field_list[deposition_type];
    var $type_related_groups = $type_related_fields.parents('.form-group');
		$type_related_groups.slideDown();
    var $type_related_panel = $type_related_fields.parents('.panel-body');
		$type_related_panel.effect(
      "highlight",
			{color: "#e1efbb"},
      2500
    );
		$deposition_type_panel.children('.alert').remove('.alert');
		if (deposition_type === "proceedings") {
			$deposition_type_panel.append(tpl_flash_message.render({
        state:'info',
        message: "<strong>Proceedings:</strong> only for complete " +
          "proceedings. For contributions use Article/Conference paper."
      }));
		}
	});

  var fieldsGroup = $("#journal_title, #volume, #issue, #page_range, #article_id, #year")
    .fieldsGroup({
      onEmpty: function enableProceedingsBox() {
        $("#nonpublic_note").removeAttr('disabled');
      },
      onNotEmpty: function disableProceedingsBox() {
        $("#nonpublic_note").attr('disabled', 'true');
      }
    });

  //FIXME: hackish way to put icons next to labels since WTForms
  //           don't allow to extend the label names with pure HTML
  $("a.panel-toggle").append('<span class="caret"></span>');

  // subject field supports multiple selections
  // using the library bootstrap-multiselect
  $('#subject').attr('multiple', 'multiple').multiselect({
    maxHeight: 400,
    enableCaseInsensitiveFiltering: true
  });

  var $language = $("#language");
  var $translated_title = $("#state-group-title_translation");

  /**
   * Hide or show translated title field regarding selected language
   */
  function handleTranslatedTitle() {
    var language_value = $language.val();

    if(language_value !== 'en') {
      $translated_title.slideDown();
    }
    else {
      $translated_title.slideUp();
    }
  }

  handleTranslatedTitle();

  $language.change(function(event) {
    handleTranslatedTitle();
  });

  $("#state-group-title_arXiv").addClass("hidden");
  $("#state-group-note").addClass("hidden");
  $("#state-group-license_url").addClass("hidden");

  /**
   * Strips the prefix off the identifier.
   * @param identifier DOI/arXiv/ISBN id
   * @returns stripped identifier
   */
  function stripSourceTags(identifier) {
    var doi_prefix = /^doi:/;
    var arxiv_prefix = /^arxiv:/;

    var strippedID = identifier.replace(doi_prefix, '');
    strippedID = strippedID.replace(arxiv_prefix, '');

    return strippedID;
  }

  /**
   * Imports data using given filter.
   *
   * @param filter {Filter}
   */
  var importData = function(id, filter) {
    // if DOI field is not empty
    var url = filter.url + id;

    $.get(url, function( data ) {

      var query_status = data.query.status;

      if (query_status !== 'success' && data.source === 'database') {
        query_status = 'duplicated';
      }

      var queryMessage = getImportMessage(query_status, filter.name, id);

      if (query_status !== 'success') {
        flash_import(queryMessage);
        return;
      }

      // do the import
      var depositionType = $deposition_type.val();
      var mapping = filter.applyFilter(data, depositionType);

      var authors_widget = DEPOSIT_FORM.field_lists.authors;

      fillForm(mapping, authors_widget);

      fieldsGroup.resetState();

      flash_import(queryMessage);
    });
  };

  /**
   * Fills the deposit form according to schema in dataMapping
   *
   * @param dataMapping {} dictionary with schema 'field_id: field_value', and
   *  special 'contributors' key to extract them to authors field.
   * @param authorsWidget interface to widget with authors fields returned by
   *  fieldlist jQuery plugin from invenio deposit's form.js
   */
  function fillForm(dataMapping, authorsWidget) {

    $.map(dataMapping, function(value, field_id){
      var $field = $('#' + field_id);
      if ($field) {
        $field.val(value);
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


  $("#importData").click(function(event) {

    var btn = $(this);
    btn.button('loading');

    var arxiv_id_value = stripSourceTags($arxiv_id_field.val());
    var doi_value = stripSourceTags($doi_field.val());

    if (!!arxiv_id_value && !!doi_value) {
      importData(arxiv_id_value, arxivFilter);
      importData(doi_value, doiFilter);
    }
    else if (!!doi_value) {
        importData(doi_value, doiFilter);
    }
    else if (!!arxiv_id_value) {
      importData(arxiv_id_value, arxivFilter);
    }
    else if (!!$isbn_field.val()) {
      // if DOI and ArXiv fields are empty and ISBN has something
      flash_import({
        state: 'info',
        message: 'The ISBN importing is not available at the moment.'
      });
    }

    btn.button('reset');
  });

	/**
	* Flash a message in the top.
	*/
	function flash_import(ctx) {
	  $('#flash-import').append(tpl_flash_message.render(ctx));
	  $('#flash-import').show('fast');
	}
});
