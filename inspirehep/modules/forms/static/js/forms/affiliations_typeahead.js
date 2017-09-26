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
  'typeahead',
], function($, jQueryPlugin, Bloodhound) {

  function AffiliationsTypeahead($element) {

    this.dataEngine = new Bloodhound({
      name: 'affiliations',
      remote: {
        url: '/api/institutions/_suggest?affiliation=%QUERY',
        filter: function(response) {
          return $.map(response.affiliation[0].options, function(el) { return el.payload });
        }
      },
      datumTokenizer: function() {},
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 100,
    });

    this.dataEngine.initialize();
    this.$element = $element;

    var suggestionTemplate = Hogan.compile(
      '<strong>{{ legacy_ICN }}</strong><br>' +
      '<small>' +
      '{{#ICN}}{{#show_future_name}}Alternative name: {{future_name}}<br>{{/show_future_name}}{{/ICN}}' +
      '{{#institution_name}}{{ institution_name }}{{/institution_name}}' +
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
        return data.legacy_ICN;
      },
      templates: {
        empty: function(data) {
          return 'Cannot find this affiliation in our database.';
        },
        suggestion: function(data) {
          function _getICN() {
            if (!data.ICN) {
              return;
            }
            for (let i=0; i<data.ICN.length; i++) {
              if (data.ICN[i] !== data.legacy_ICN) {
                return data.ICN[i];
              }
            }
          }
          let ICN = _getICN();
          if (ICN) {
            data.show_future_name = true;
            data.future_name = ICN;
          }

          if (data.institution_names && data.institution_names.length > 0) {
            data.institution_name = data.institution_names[0];
          }
          return suggestionTemplate.render.call(suggestionTemplate, data);
        }.bind(this)
      }
    });

    return $element;
  }

  $.fn.affiliationsTypeahead = jQueryPlugin(AffiliationsTypeahead, 'affiliation-typeahead');

  return AffiliationsTypeahead;
});
