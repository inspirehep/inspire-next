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
  var DataSource = require("js/literaturesuggest/data_sources/data_source");
  var isbnSource = new DataSource({

    id: 'isbn',
    name: 'ISBN',
    service: 'ISBN',

  });

  isbnSource.importData = function(id) {
    return {
      statusMessage: {
        state: 'info',
        message: 'The ISBN import is not available at the moment.'
      }
    };
  };
  module.exports = isbnSource;
});
