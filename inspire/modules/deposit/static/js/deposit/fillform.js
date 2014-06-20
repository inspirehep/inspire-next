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

    $("#journal_title, #volume, #issue, #page_range, #article_id, #year")
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

  function Filter(options) {

    /**
     *
     * @type {{}}
     */
    this.common_mapping = options.common_mapping ?
      options.common_mapping : function(data) {};

    /**
     *
     * @type {function} The function should return:
     */
    this.special_mapping = options.special_mapping ?
      options.special_mapping : {};

    /**
     * Function to extract author sub-form content having
     * an item from
     */
    this.extract_contributor = options.extract_contributor ?
      options.extract_contributor : function(contributor) {};

    /**
     * Filter name. It will be displayed in info messages.
     *
     * @type {string}
     */
    this.name = options.name ? options.name : '';

    /**
     * Query url.
     *
     * @type {string}
     */
    this.url = options.url ? options.url : '';
  }

  var doiFilter = new Filter({
    name: 'DOI',
    url: '/deposit/search_doi?doi=',

    common_mapping: function(data) {

      var page_range;

      if (data.first_page && data.last_page) {
        page_range = data.first_page + "-" + data.last_page;
      }

      return {
        journal_title: data.journal_title,
        isbn: data.isbn,
        page_range: page_range,
        volume: data.volume,
        year: data.year,
        issue: data.issuess,
        contributors: data.contributors
      };
    },

    special_mapping: {
      thesis: function(data) {
        return {
          title: data.volume_title
        };
      },
      article: function(data) {
        return {
          title: data.article_title
        };
      }
    },

    extract_contributor: function(contributor) {
      var name, surname;

      if (contributor.contributor[0]) {
        name = contributor.contributor[0].given_name;
      }

      if (contributor.contributor[1]) {
        surname = contributor.contributor[1].surname;
      }

      return {
        name: name + ', ' + surname,
        affiliation: ''
      };
    }
  });

  var arxivFilter = new Filter({
    name: 'arXiv',
    url: '/arxiv/search?arxiv=',

    special_mapping: {
      article: function(data) {
        return {
          title: data.title,
          year: data.published,
          abstract: data.summary,
          article_id: data.id,
          contributors: data.author
        };
      }
    },

    extract_contributor: function(contributor) {

      return {
        name: contributor.name,
        affiliation: ''
      };
    }
  });

  /**
   * Generates the import status message.
   * @param queryStatus
   * @param idType DOI/arXiv/ISBN etc.
   * @param id
   * @returns {{state: string, message: string}} as in the input of
   *  tpl_flash_message template
   */
  function getImportMessage(queryStatus, idType, id) {
    if (queryStatus === 'notfound') {
      return {
        state: 'warning',
        message: 'The ' + idType + ' ' + id + ' was not found.'
      };
    }
    if(queryStatus === 'malformed') {
      return {
        state: 'warning',
        message: 'The ' + idType + ' ' + id + ' is malformed.'
      };
    }
    if (queryStatus === 'success') {
      return {
        state: 'success',
        message: 'The data was successfully imported.'
      };
    }
    if (queryStatus === 'duplicated') {
      return {
        state: 'info',
        message: 'This ' + idType + ' already exists in Inspire database.'
      };
    }

    return {
      state: 'warning',
      message: 'Unknown import result.'
    };
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
      var deposition_type = $deposition_type.val();

      var common_mapping = filter.common_mapping(data.query);
      var special_mapping = {};
      if (filter.special_mapping[deposition_type]) {
        special_mapping = filter.special_mapping[deposition_type](data.query);
      }

      var mapping = $.extend({}, common_mapping, special_mapping);

      $.map(mapping, function(value, field_id){
        var $field = $('#' + field_id);
        if ($field) {
          $field.val(value);
        }
      });

      var contributors = $.map(mapping.contributors, filter.extract_contributor);
      var authors_widget = DEPOSIT_FORM.field_lists.authors;

      // ensure there is a one empty field
      if (authors_widget.get_next_index() === 0) {
        authors_widget.append_element();
      }

      for (var i in contributors) {
        authors_widget.set_element_values(i, contributors[i]);
        // next index is i+1 but there should stay one empty field
        if (parseInt(i) + 2 > authors_widget.get_next_index()) {
          authors_widget.append_element();
        }
      }

      flash_import(queryMessage);
    });
  };

	$("#importData").click(function(event) {

    var btn = $(this);
		btn.button('loading');

		if (!!$doi_field.val()) {
			importData($doi_field.val(), doiFilter);
		}
		else if (!!$arxiv_id_field.val()) {
		  importData($arxiv_id_field.val(), arxivFilter);
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
	  $('#flash-import').html(tpl_flash_message.render(ctx));
	  $('#flash-import').show('fast');
	}
});
