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
  'js/search/default_typeahead_configuration'
], function(getDefaultParserConf) {

  return function getInvenioSpiresParserConf(area_keywords) {

    var invenio_parser_options = getDefaultParserConf(area_keywords).invenio;

    var invenio_get_next_word = invenio_parser_options.get_next_word_type;

    invenio_parser_options.get_next_word_type = function(previous_word_type, word_types) {

      if (previous_word_type == undefined)
        return [].concat(invenio_get_next_word(previous_word_type, word_types))
          .concat(word_types.SPIRES_SWITCH);
      if (previous_word_type == word_types.SPIRES_SWITCH)
        return invenio_get_next_word(undefined, word_types);

      return invenio_get_next_word(previous_word_type, word_types);
    }

    function notEndsWithColon(str, char_roles, end_idx) {
      return str[end_idx] != ':';
    }

    function endsWithColon(str, char_roles, end_idx) {
      return str[end_idx] == ':';
    }

    function notStartsNorEndsWithColon(str, char_roles, start_idx, keyword) {
      return notEndsWithColon(str, char_roles, start_idx + keyword.length)
        && !(start_idx > 0 && str[start_idx - 1] == ':');
    }

    function isFirstWord(str, char_roles, start_idx, keyword) {

      if (start_idx == 0)
        return true;
      do {
        start_idx--;
      } while (char_roles[start_idx] == 'SEPARATOR' && start_idx >= 0);
      return start_idx == 0;
    }

    function setSpireSyntax(search_typeahead) {
      search_typeahead.setOptions('spires');
    }

    var spires_switch_conf = {
      min_length: 1,
      keyword_function: setSpireSyntax,
      detection_condition: function(str, char_roles, start_idx, keyword) {
        return isFirstWord(str, char_roles, start_idx, keyword)
          && notStartsNorEndsWithColon(str, char_roles, start_idx, keyword)
      },
      values: ['find'],
      autocomplete_suffix: ' '
    }

    invenio_parser_options.keywords.SEARCH['SPIRES_SWITCH'] = spires_switch_conf;

    var spires_parser_options = {
      keywords: {
        SEARCH: {
          SPIRES_SWITCH: spires_switch_conf,
          LOGICAL_EXP: {
            min_length: 1,
            values: ['and', 'or'],
            autocomplete_suffix: ' '
          },
          NOT: {
            min_length: 1,
            values: ['not'],
            autocomplete_suffix: ' '
          }
        },
        ORDER: {
          QUERY_TYPE: {
            min_length: 1,
            values: ['a', 'aff', 'j', 'c', 'refersto'],
            autocomplete_suffix: ' '
          },
          QUERY_VALUE: {
            min_length: 3
          }
        }
      },
      separators: [' ', '(', ')'],
      value_type_interpretation: {
        a: 'exactauthor'
      },
      get_next_word_type: invenio_parser_options.get_next_word_type
    };

    return {
      invenio: invenio_parser_options,
      spires: spires_parser_options
    }

  }
});
