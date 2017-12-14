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
  'jquery',
  'js/jquery_plugin',
], function($, jQueryPlugin) {

  function ConferencesTypeahead($element) {
    this.dataEngine = new Bloodhound({
      name: 'conferences',
      remote: {
        url: '/api/conferences/_suggest?conference=%QUERY',
        filter: function(response) {
          return response.conference[0].options;
        }
      },
      datumTokenizer: function() {},
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 100,
    });

    this.dataEngine.initialize();
    this.$element = $element;

    var suggestionTemplate = Hogan.compile(
      '<strong>{{#text}} {{ text }} {{/text}}</strong><br>' +
        '<small>' +
        '{{#payload.opening_date}} {{ payload.opening_date }}, {{/payload.opening_date}}' +
        '{{#payload.city}} {{ payload.city }}, {{/payload.city}} ' +
        '{{#payload.country}} {{ payload.country }} {{/payload.country}}<br>' +
        '{{#payload.cnum}} {{ payload.cnum }} {{/payload.cnum}}<br>' +
        '</small>'
    );

    this.$element.typeahead({
      minLength: 3
    }, {
      // after typeahead upgrade to 0.11 can be substituted with:
      // source: this.engine.ttAdapter(),
      // https://github.com/twitter/typeahead.js/issues/166
      source: function(query, callback) {
        // trigger can be deleted after typeahead upgrade to 0.11
        this.$element.trigger('typeahead:asyncrequest');
        this.dataEngine.get(query, function(suggestions) {
          this.$element.trigger('typeahead:asyncreceive');
          callback(suggestions);
        }.bind(this));
      }.bind(this),
      displayKey: function(data) {
        return data.text;
      },
      templates: {
        empty: function(data) {
          return 'Cannot find this conference in our database.';
        },
        suggestion: function(data) {
          return suggestionTemplate.render.call(suggestionTemplate, data);
        }.bind(this)
      }
    });

    return $element;
  }

  $.fn.conferencesTypeahead = jQueryPlugin(ConferencesTypeahead, 'conference-typeahead');

  return ConferencesTypeahead;
});
