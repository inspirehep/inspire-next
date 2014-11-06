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
  'jquery'
], function($) {

  function jQueryPlugin(constructor, dataLabel) {

    return function(options) {

      var $elements = this;

      return $elements.map(function (idx, element) {
        var $element = $(element);
        var object = $element.data(dataLabel);
        var _options = (typeof options === 'object' && options);
        // attach jQuery plugin
        if (!object) {
          object = new constructor($element, _options);
          $element.data(dataLabel, object);
          if (object.init) {
            object.init();
          }
          if (object.connectEvents) {
            object.connectEvents();
          }
        }
        return object;
      });
    }
  }

  return jQueryPlugin;
});
