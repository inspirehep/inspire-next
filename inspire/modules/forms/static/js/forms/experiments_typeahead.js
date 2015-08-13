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
        url: '/search?cc=Experiments&p=experimentautocomplete:/.*%QUERY.*/&of=recjson&rg=100',
        replace: function(url, query) {
          // Names of Experiments are separated by dashes
          // Break into components so that we match the indexed values (where
          // dashes are removed)
          var query_components = query.toLowerCase().split("-");
          var pattern = "";
          $.each(query_components, function(index) {
            if (index != 0) {
              pattern = pattern + " AND ";
            }
            pattern = pattern + "experimentautocomplete:" + "/" + this + ".*/";
          })

          return '/search?cc=Experiments&p=' + pattern + '&of=recjson&rg=100'
        },
        filter: function(response) {
          return response.sort(function(a, b){
            if(a.experiment_name < b.experiment_name) return -1;
            if(a.experiment_name > b.experiment_name) return 1;
            return 0;
          })
        }
      },
      datumTokenizer: function() {},
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 100,
    });

    this.dataEngine.initialize();
    this.$element = $element;

    var suggestionTemplate = Hogan.compile(
      '<strong>{{ experiment_name }}</strong><br>'
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
      displayKey: 'experiment_name',
      templates: {
        empty: function(data) {
          return 'Cannot find this experiment in our database.';
        },
        suggestion: function(data) {
          return suggestionTemplate.render.call(suggestionTemplate, data);
        }.bind(this)
      }
    });

    return $element;
  }

  $.fn.experimentsTypeahead = jQueryPlugin(ExperimentsTypeahead, 'experiment-typeahead');

  return ExperimentsTypeahead;
});
