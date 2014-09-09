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


define(function(require, exports, module) {

  function DataMapper(options) {

    /**
     * Mapping format:
     *
     * {
     *   fieldId: String,
     *   fieldId: String,
     *   fieldId: String
     * },
     */

    /**
     * Mapping common to every type of deposition.
     * @type {function} returns the 'Mapping format'
     */
    this.common_mapping = options.common_mapping ?
      options.common_mapping : function(data) {};

    /**
     *
     * @type {{deposition_type: function}} The function should return
     *   the 'Mapping format'
     */
    this.special_mapping = options.special_mapping ?
      options.special_mapping : {};

    /**
     * Function to extract author sub-form content having
     * an item from should return
     * {
     *   name: String,
     *   affiliation: String
     * }
     */
    this.extract_contributor = options.extract_contributor ?
      options.extract_contributor : function(contributor) {
        return contributor;
    };
  }

  DataMapper.prototype = {

    /**
     * Maps data to a common format in the way defined in filter.
     *
     * @param data {*} data to map
     * @param depositionType {String} type of deposition
     * @returns {*}
     */
    map: function(data, depositionType) {
      var common_mapping = this.common_mapping(data);
      var special_mapping = {};
      if (this.special_mapping[depositionType]) {
        special_mapping = this.special_mapping[depositionType](data);
      }

      var mapping = $.extend({}, common_mapping, special_mapping);
      if (mapping.authors) {
        mapping.authors = $.map(mapping.authors, this.extract_contributor);
      }

      return mapping;
    }
  };

  module.exports = DataMapper;
});
