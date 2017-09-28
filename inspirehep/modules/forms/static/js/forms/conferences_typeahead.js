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

define([
  'js/forms/extended_typeahead'
], function(ExtendedTypeahead) {

  function conferencesTypeahead($element) {
    $element.extendedTypeahead({
      suggestionTemplate: Hogan.compile(
        '<b>{{ title }}</b><br>' +
        '<small>' +
        '{{ opening_date }}, {{ city }}, {{ country }}<br>' +
        '{{ cnum }}' +
        '</small>'
      ),
      selectedValueTemplate: Hogan.compile(
        '{{ title }}, {{ opening_date }}, {{ city }}, {{ country }}'
      ),
      cannotFindMessage: 'Cannot find this conference in our database.',
      extractRawValue: function(data) {
        return data.cnum;
      },
      displayKey: null,
      displayfn: function(obj) {
        return obj;
      },
      dataEngine: new Bloodhound({
        name: 'conferences',
        remote: {
          url: '/api/conferences?q=conferenceautocomplete:%QUERY*',
          filter: function(response) {
            return $.map(response.hits.hits, function(el) {
              el.metadata.city = el.metadata.address[0].cities[0];
              el.metadata.country = el.metadata.address[0].country_code;
              el.metadata.title = el.metadata.titles[0].title;
              return el.metadata
            }).sort(function(x, y) {
              return new Date(y.opening_date) - new Date(x.opening_date);
            });
          }
        },
        datumTokenizer: function() {},
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 100,
      })
    });

    return $element;
  }

  return conferencesTypeahead;
});
