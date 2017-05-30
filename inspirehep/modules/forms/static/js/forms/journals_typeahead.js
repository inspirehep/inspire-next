/*
 * This file is part of INSPIRE.
 * Copyright (C) 2015 CERN.
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

  function JournalsTypeahead($element) {

    this.dataEngine = new Bloodhound({
      name: 'journals',
      remote: {
        url: '/api/journals/_suggest?journal_title=%QUERY',
        filter: function(response) {
          return $.map(response.journal_title[0].options, function(el) { return el });
        }
      },
      datumTokenizer: function() {},
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 100,
    });

    this.dataEngine.initialize();
    this.$element = $element;

    var suggestionTemplate = Hogan.compile(
      '<strong>{{ short_title }}</strong><br>' +
      '<small>{{ title }}</small>'
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
          return 'Cannot find this journal in our database.';
        },
        suggestion: function(data) {
          var metadata = {};
          metadata['title'] = data.payload.full_title;
          metadata['short_title'] = data.text;
          return suggestionTemplate.render.call(suggestionTemplate, metadata);
        }.bind(this)
      }
    });

    return $element;
  }

  $.fn.journalsTypeahead = jQueryPlugin(JournalsTypeahead, 'journal-typeahead');

  return JournalsTypeahead;
});
