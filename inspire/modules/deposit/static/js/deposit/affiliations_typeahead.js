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

  function AffiliationsTypeahead($element) {

    this.dataEngine = new Bloodhound({
      name: 'affiliations',
      remote: {
        url: '/search?cc=Institutions&p=affautocomplete:/%QUERY.*/&of=recjson&rg=100',
        replace: function(url, query) {
          var query_components = query.toLowerCase().split(" ");
          var pattern = "";
          $.each(query_components, function(index) {
            if (index != 0) {
              pattern = pattern + " AND ";
            }
            pattern = pattern + "affautocomplete:" + "/" + this + ".*/";
          })

          return '/search?cc=Institutions&p=' + pattern + '&of=recjson&rg=100'
        },
        filter: function(response) {
          var affiliations = $.map(response, function(item, idx) {
            return item.institution;
          });
          return affiliations.sort(function(a, b){
            if(a.affiliation < b.affiliation) return -1;
            if(a.affiliation > b.affiliation) return 1;
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
      '<strong>{{ affiliation }}</strong><br>' +
      '<small>' +
      '{{#new_name}}{{#show_future_name}}Alternative name: {{new_name}}<br>{{/show_future_name}}{{/new_name}}' +
      '{{#department}}{{ department }}<br>{{/department}}' +
      '{{#name}}{{ name }}{{/name}}' +
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
      displayKey: 'affiliation',
      templates: {
        empty: function(data) {
          return 'Cannot find this affiliation in our database.';
        },
        suggestion: function(data) {
          if (data.new_name != data.affiliation) {
            data.show_future_name = true;
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
