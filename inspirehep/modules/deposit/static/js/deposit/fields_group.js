/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014, 2016 CERN.
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
  /**
   * Allows to trigger actions when all the fields from
   * the selector are empty, and when at least one of them is filled
   */
  var $ = require("jquery"),
    buckets = require("bucketsjs");

  /**
   * Constructor.
   *
   * @param fields DOM/jQuery objects belonging to the group
   * @param options dictionary
   * @constructor
   */
  function FieldsGroup(fields, options) {

    // ensure that there is jQuery selector available
    this.$fields = $(fields);
    this.options = $.extend({}, $.fn.fieldsGroup.defaults, options);

    this.onEmpty = this.options.onEmpty;
    this.onNotEmpty = this.options.onNotEmpty;
  }

  FieldsGroup.prototype = {

    init: function() {
      this.resetState();
    },

    /**
     * Connecting events to functions, separated just to have them in one
     * place.
     */
    connectEvents: function() {

      // to have access to the class inside the events
      var that = this;

      $.each(this.$fields, function() {
        $(this).on('keyup', function(event) {
          that.updateState($(this));
        });
      });
    },

    isFieldFilled: function($field) {
      return !!$.trim($field.val()).length;
    },

    /**
     * Goes through the fields and checks if they are filled.
     */
    resetState: function() {
      var that = this;

      this.filledFields = new buckets.Set();

      $.each(this.$fields, function() {
        var $field = $(this);
        if (that.isFieldFilled($field)) {
          that.filledFields.add($field.attr('id'));
        }
      });

      if (this.filledFields.isEmpty()) {
        this.onEmpty();
      } else {
        this.onNotEmpty();
      }
    },

    /**
     * Updates the state after modifying one field and triggers functions
     * appropriate to the state.
     *
     * @param $modified_field {jQuery object} the modified field
     */
    updateState: function($modified_field) {
      var fieldId = $modified_field.attr('id');
      var wasFilled = this.filledFields.contains(fieldId);
      var isFilled = this.isFieldFilled($modified_field);

      if (isFilled === wasFilled) {
        return;
      }

      var fieldsWereEmpty = this.filledFields.isEmpty();

      if (!isFilled && wasFilled) {
        this.filledFields.remove(fieldId);
      } else if (isFilled && !wasFilled) {
        this.filledFields.add(fieldId);
      }

      var fieldsAreEmpty = this.filledFields.isEmpty();

      if (fieldsWereEmpty && !fieldsAreEmpty) {
        this.onNotEmpty();
      }
      if (!fieldsWereEmpty && fieldsAreEmpty) {
        this.onEmpty();
      }
    }
  };


  $.fn.fieldsGroup = function(options) {

    var $fields = this;
    var data = new FieldsGroup($fields, options);

    this.each(function() {
      var $this = $(this);
      // attach jQuery plugin
      if (!$this.data('fields-group')) {
        $this.data('fields-group', data);
      }
    });

    data.init();
    data.connectEvents();

    return data;
  };

  $.fn.fieldsGroup.defaults = {

    /**
     * @param onEmpty {function} triggered when all fields are empty
     */
    onEmpty: function() {},

    /**
     * @param onNotEmpty {function} triggered when the first field gets
     *  filled
     */
    onNotEmpty: function() {},
  };

});
