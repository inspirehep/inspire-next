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
  var $ = require("jquery");
  var jQueryPlugin = require('js/jquery_plugin');
  
  var MessageBox = (function() {

    /**
     * Constructor.
     *
     * @param element html element on which the plugin
     * @param options dictionary
     * @constructor
     */
    function MessageBox(element, options) {

      // ensure that there is jQuery selector available
      this.$element = $(element);
      this.options = $.extend({}, $.fn.messageBox.defaults, options);

      this.template = this.options.hoganTemplate;

    }

    MessageBox.prototype = {

      /**
       * Appends one message. Use append which is more universal.
       * @param ctx
       * @private
       */
      _appendOne: function(ctx) {
        this.$element.append(this.template(ctx));
        this.$element.show('fast');
      },

      /**
       * Cleans the message box.
       */
      clean: function() {
        this.$element.empty();
      },

      /**
       * Appends one or more messages to the array box.
       * @param messages can be a single message context or an array of them.
       */
      append: function(messages) {
        if (!Array.isArray(messages)) {
          this._appendOne(messages);
        }
        var that = this;
        $.each(messages, function() {
          that._appendOne(this);
        });
      }
    };

    return MessageBox;

  })();

  $.fn.messageBox = jQueryPlugin(MessageBox, 'message-box');

  $.fn.messageBox.defaults = {
    /**
     * @param the template used to render a message. Should have parameters
     *  'state' and 'message'.
     */
    hoganTemplate: {},
  };

});
