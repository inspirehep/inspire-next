/*
 * This file is part of Invenio.
 * Copyright (C) 2014, 2015 CERN.
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


define([
  'jquery',
  'searchtypeahead-configuration',
  'typeahead',
  'js/search/typeahead',
], function($, getParserConf, Bloodhound) {
  "use strict";

  $("form[name=search]").submit(function() {
    $(this).children(':input[value=""]').attr("disabled", "disabled");
    $('.add_to_search-form').remove()
    return true; // ensure form still submits
  })

  $("button[name=action_search]").on("click", function() {
    $("input[name=post_filter]").val('');
  })

  // ------------ typeahead for "Add to search" form ----------------

  $('[data-provide="typeahead-url"]').each(function(index, elem) {

    var field = $(elem),
      source = field.data('source')

    var engine = new Bloodhound({
      datumTokenizer: function(d) {
        return Bloodhound.tokenizers.whitespace(d.value)
      },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 10,
      remote: {
        url: source,
        replace: function(url, query) {
          return url + '?q=' + query
        },
        filter: function(response) {
          return response.results
        }
      }
    })

    engine.initialize()

    field.typeahead({
      minLength: 3
    }, {
      source: engine.ttAdapter(),
      displayKey: 'value'
    })
  })

  //---------------------

  return function(form) {

    var operators = {
        'a': 'AND ',
        'o': 'OR ',
        'n': 'AND NOT '
      },
      // the visible search field
      searchQueryField = $('form[name=search] input[name=p]'),
      // all fields containg search query, there are some hidden ones too
      allSearchQueryFields = $('[name=p]')

    /**
     * Sets value of the main search field. Should be used
     * instead of jQuery's val() to update typeahead's
     * internal query.
     *
     * @method setSearchFieldValue
     * @param {String} val value to be set
     */
    function setSearchFieldValue(val) {
      searchQueryField.data('search_typeahead').setFieldValue(val)
      allSearchQueryFields.val(val)
    }

    /**
     * Removes query value from 'what?' field in 'advanced' tab
     *
     * @method cleanAdvancedQuery
     */
    function cleanAdvancedQueryForm() {
      $('[name=p1]').val('')
    }

    /**
     * Removes query values from all fields in 'simple' tab
     *
     * @method cleanSimpleQueryForm
     */
    function cleanSimpleQueryForm() {
      $(':focus').blur()
      $('#simple-search input').val('')
    }

    /**
     * Creates search query from 'simple' tab in 'Add to search' form
     *
     * @method getSimpleQuery
     * @returns {String} query from the form content
     *
     */
    function getSimpleQuery() {
      var query_str = '';

      // get values
      var p = $('[name=p]'),
        query = [],
        op1 = $('#add_type-btn-group .active').children(':first').val(),
        author = $('#author').val(),
        title = $('#title').val(),
        rn = $('#rn').val(),
        aff = $('#aff').val(),
        cn = $('#cn').val(),
        k = $('#k').val(),
        //eprinttype = $('#eprint-type').val(),
        //eprintnumber = $('#eprint-number').val(),
        j = $('#journal-name').val(),
        jvol = $('#journal-vol').val(),
        jpage = $('#journal-page').val(),
        //match every word or the whole sentence in the quotes
        matcher = /("(?:[^"\\]|\\.)*")|('(?:[^'\\]|\\.)*')|(\S+)/g

      function buildQueryElement(fieldName, input, reg) {
        reg = reg ? reg : matcher;
        var matches = input.match(reg);

        return $.map(matches, function(item) {
          return fieldName + item;
        }).join(" " + operators[op1] + " ");
      }

      if (author !== '') {
        query.push('author:' + '\"' + author + '\"');
      }
      if (title !== '') {
        query.push('title:' + '\"' + title + '\"');
      }
      if (rn !== '') {
        query.push(buildQueryElement("reportnumber:", rn));
      }
      if (aff !== '') {
        query.push(buildQueryElement("affiliation:", aff));
      }
      if (cn !== '') {
        query.push(buildQueryElement('collaboration:', cn));
      }
      if (k !== '') {
        query.push(buildQueryElement('keyword:', k));
      }

      if (j !== '') {
        query.push('journal:' + j);
      }
      if (jvol !== '') {
        query.push('909C4v:' + jvol);
      }
      if (jpage !== '') {
        query.push('909C4c:' + jpage);
      }

      if (query.length > 0) {
        query_str = query.join(' ' + operators[op1]);
      }

      return query_str;
    }

    /**
     * Updates query value in the search field
     *
     * @method makeSearchQuery
     */
    function makeSearchQuery() {
      var active_tab = $('.add_to_search-form .tab-buttons li.active a').attr('href');

      if (active_tab === '#simple-search') {
        var current_query = $.trim(searchQueryField.val())
        var new_part = getSimpleQuery()
        setSearchFieldValue(mergeQuery(current_query, new_part))
        cleanSimpleQueryForm()
      } else {
        addAdvancedQueryToSearch()
        $('.add_to_search-form .appender').trigger('click')
      }
    }

    // search buttons
    $('.add_to_search-form button[name=action_search]').on('click', function(e) {
      makeSearchQuery()
      e.stopPropagation()

    })


    $('.add_to_search-form #advanced-search input, .add_to_search-form #simple-search input').keypress(function(event) {
      // on 'return' key
      if (event.which == 13) {
        makeSearchQuery()
        return false
      }
    })

    $('.add_to_search-form #advanced-search .appender').on('click', function(e) {
      var op1 = $('#add_type-btn-group .active').children(':first').val(),
        btn = $(this),
        source = $('[name=' + btn.data('source') + ']'),
        target = $('[name=' + btn.data('target') + ']'),
        val = $.trim(target.val()),
        op = (op1 == 'a' && val === '') ? '' : operators[op1]

      if (val !== '') {
        val += ' ' + op
      }
      if (source.val().length > 0) {
        target.val(val + source.attr('name') + ':"' + source.val() + '"')
        source.val('')
      }
      e.stopPropagation()
      return false
    })

    // -------------- SEARCH FIELD TYPEAHEAD ----------------

    var InvenioKeywords = form.invenio_keywords;
    var SpiresKeywords = form.spires_keywords;

    $('form[name=search] input[name=p]').searchTypeahead({
      value_hints_url: form.hintsUrl,
      options_sets: getParserConf(InvenioKeywords, SpiresKeywords),
      default_set: form.defaultSet
    })
  }
})
