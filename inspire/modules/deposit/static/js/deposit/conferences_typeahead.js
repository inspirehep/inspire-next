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
  'js/deposit/extended_typeahead'
], function(ExtendedTypeahead) {

  function conferencesTypeahead($element) {
    $element.extendedTypeahead({
      suggestionTemplate: Hogan.compile(
        '<b>{{ title }}</b><br>' +
        '<small>' +
        '{{ opening_date }}, {{ place }}<br>' +
        '{{ cnum }}' +
        '</small>'
      ),
      selectedValueTemplate: Hogan.compile(
        '{{ title }}, {{ opening_date }}, {{ place }}'
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
          url: '/search?cc=Conferences&p=conferenceautocomplete:%QUERY*&of=recjson',
          replace: function(url, query) {
            var query_components = query.toLowerCase().split(" ");
            var pattern = "";
            $.each(query_components, function(index) {
              if (index != 0) {
                pattern = pattern + " AND ";
              }
              pattern = pattern + "conferenceautocomplete:" + "/" + this + ".*/";
            })

            return '/search?cc=Conferences&p=' + pattern + '&of=recjson&rg=100'
        },
        filter: function(response) {
          response = response.sort(function(a, b) {
            if(a.title < b.title) return -1;
            if(a.title > b.title) return 1;
            return 0;
          });
          return response;
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
