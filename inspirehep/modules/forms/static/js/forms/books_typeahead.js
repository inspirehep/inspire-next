/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014-2017 CERN.
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
 * In applying this license, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

define([
  'js/forms/extended_typeahead'
], function(ExtendedTypeahead) {

  function booksTypeahead($element) {
    $element.extendedTypeahead({
      suggestionTemplate: Hogan.compile(
        '<b>{{ title }}</b><br>' +
        '<small>' +
        '{{ author_list }}<br>' +
        '</small>'
      ),
      selectedValueTemplate: Hogan.compile(
        '{{ title }}'
      ),
      cannotFindMessage: 'Cannot find this book in our database.',
      extractRawValue: function(data) {
        return data.control_number;
      },
      displayKey: null,
      displayfn: function(obj) {
        return obj;
      },
      dataEngine: new Bloodhound({
        name: 'books',
        remote: {
          url: '/api/literature/_suggest?book_title=%QUERY',
          filter: function(response) {
            return $.map(response.book_title[0].options, function(el) {
              el.et_al = '';
              if (typeof el.payload.title !== 'undefined'){
                el.title = el.payload.title[0];
              }
              if (typeof el.payload.authors !== 'undefined'){
                  el.author_list = el.payload.authors.slice(0,2).map(function(a) {return a.replace(',', '') }).toString().replace(',',', ');
                  if( el.payload.authors.length > 3 ) {
                    el.et_al = 'et al.';
                  }
                }
              return el
            })
          }
        },
        datumTokenizer: function() {},
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 10,
      })
    });

    return $element;
  }

  return booksTypeahead;
});
