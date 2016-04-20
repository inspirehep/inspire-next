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
  'js/jquery_plugin'
], function($, jQueryPlugin) {

  /**
   * Useful for a form field with appied js scripts, which changes its value in
   * a way that it doesn't correspond to what should be send on submit.
   * The original field gets/is hidden, and the frontend field does the role of
   * communication with a user while the hidden (original) one is the one which
   * is going to be sent on submit.
   * If the frontend field is not provided a it is created as a copy of
   * the original one and appended just on its place.
   */
  function SynchronizedField($element, options) {

    options = $.extend({}, $.fn.synchronizedField.defaults, options);

    this.$originalField = $element;
    this.$form = this.$originalField.parents('form');
    this.$frontendField = options.$frontendField;
    this.isOriginalFieldCloned = false;
    this.synchronizationEvents = options.synchronizationEvents;
    this.synchronizationFn = options.synchronizationFn;
    this.resetValueOnSubmit = options.resetValueOnSubmit;
    this.propagatedEvents = options.propagatedEvents;
    this.initializationFn = options.initializationFn;
    this.reverseSynchronizationFn = options.reverseSynchronizationFn;
    this.debug = options.debug;
  }

  SynchronizedField.prototype = {

    init: function() {
      if (!this.$frontendField) {
        cloneOriginalField();
      }
      if (!this.debug) {
        this.$originalField.hide();
      }
      this.initializationFn(this.$frontendField);
      this.reverseSynchronizationFn(this.$originalField, this.$frontendField);
    },

    destroy: function() {
      // TODO: unbind events - this should allow to delete the frontend field
      // on submit and revert it back if submit fails
      this.synchronizationFn(this.$originalField, this.$frontendField);
      this.$frontendField.remove();
      this.$originalField.show();
    },

    connectEvents: function() {
      if (this.synchronizationEvents) {
        this.$frontendField.on(this.synchronizationEvents, function(event) {
          this.synchronizationFn(this.$originalField, this.$frontendField);
        }.bind(this));
      }

      // always synchronizes values on submit
      this.$form.on('submit', function() {
        this.synchronizationFn(this.$originalField, this.$frontendField);
        if (this.resetValueOnSubmit) {
          this.$frontendField.val('');
        }
      }.bind(this));

      if (this.propagatedEvents) {
        this.$frontendField.on(this.propagatedEvents, function(event) {
          this.$originalField.trigger(event);
        }.bind(this));
      }
    },

    cloneOriginalField: function() {
      var $clone = this.$originalField.clone();
      $clone.removeAttr('id');
      this.$originalField.after($clone);
      this.isOriginalFieldCloned = true;
      this.$frontendField = $clone;
    }
  };

  $.fn.synchronizedField = jQueryPlugin(SynchronizedField, 'synchronized-field');

  $.fn.synchronizedField.defaults = {
    /**
     * @type {jQuery selector} optional; The field used as the one shown to 
     *  a user. If not defined then it will be created as a copy of the original
     *  one.
     */
    $frontendField: null,
    /**
     * @type {String} events of the frontend field on which the value at the
     *  original hidden field will be updated; space-separated.
     */
    synchronizationEvents: null,
    /**
     * @type {function} initialization function for frontend field.
     */
    initializationFn: function($frontendField) {},
    /**
     * @type {function} a function to update the original field value basing on
     *  the frontend one. Used for value synchronization on synchronization
     *  events.
     */
    synchronizationFn: function($originalField, $frontendField) {
      $originalField.val($frontendField.val());
    },
    /**
     * @type {function} a function to update the frontend field value basing on
     *  the original one. Used for initialization from a field with non-empty
     *  value.
     */
    reverseSynchronizationFn: function($originalField, $frontendField) {
      $frontendField.val($originalField.val());
    },
    /**
     * @type {Boolean} if true the frontend field value will be set to an empty
     *  string on submit event.
     */
    resetValueOnSubmit: false,
    /**
     * @type {String} events propagated from the frontend field to the original 
     *  one; space-separated.
     */
    propagatedEvents: null,
    /**
     * @type {Boolean} show the hidden field for debugging purposes.
     */
    debug: false,
  };

  return SynchronizedField;
});
