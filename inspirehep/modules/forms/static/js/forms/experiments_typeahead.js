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

  function ExperimentsTypeahead($element) {

    this.dataEngine = new Bloodhound({
      name: 'experiments',
      remote: {
        url: '/api/experiments?q=experimentautocomplete:%QUERY*',
        filter: function(response) {
          return response.hits.hits.sort(function (x, y) {
            var x_title = x.metadata.legacy_name,
                y_title = y.metadata.legacy_name;

            return x_title.localeCompare(y_title);
          });
        },
      },
      datumTokenizer: function() {},
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 20,
    });

    this.dataEngine.initialize();
    this.$element = $element;

    var suggestionTemplate = Hogan.compile(
      '<strong>{{ display_name }}</strong><br>'
    );

    this.$element.typeahead({
      minLength: 2
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
        return data.metadata.legacy_name;
      },
      templates: {
        empty: function(data) {
          return 'Cannot find this experiment in our database.';
        },
        suggestion: function(data) {
          data.metadata.display_name = data.metadata.legacy_name;
          return suggestionTemplate.render.call(suggestionTemplate, data.metadata);
        }.bind(this)
      }
    });

    return $element;
  }

  $.fn.experimentsTypeahead = jQueryPlugin(ExperimentsTypeahead, 'experiment-typeahead');

  return ExperimentsTypeahead;
});
