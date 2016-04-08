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
  "use strict";

  var $ = require('jquery');
  var tpl_flash_message = require('hgn!js/forms/templates/flash_message');
  require("js/literaturesuggest/message_box");
  require("readmore");

  function PreviewModal($element, options) {
    this.$element = $element;
    this.$acceptButton = this.$element.find('#acceptData');
    this.$rejectButton = this.$element.find('#rejectData');
    this.$table = this.$element.find('#data-table')
    this.data = {};
    this.labels = options.labels;
    this.ignoredFields = options.ignoredFields;
    this.init();
  }

  PreviewModal.prototype = {

    init: function() {
      this.messageBox = this.$element.find('#flash-import').messageBox({
        hoganTemplate: tpl_flash_message,
      })[0];
      this.connectEvents();
    },

    show: function(data) {
      this.data = data.mapping;
      this.messageBox.clean();
      if (data.statusMessages) {
        this.messageBox.append(data.statusMessages);
      }
      var cloneData = jQuery.extend(true, {}, this.data);
      this.renderModal(cloneData);
    },

    renderModal: function(dataModal) {

      if ($.isEmptyObject(dataModal)) {
        return;
      }

      var that = this;

      var tableTemplate = Hogan.compile('<table class="table table-hover"><tbody>{{{content}}}</tbody></table>');
      var rowTemplate = Hogan.compile('<tr>{{{content}}}</tr>\n');
      var cellTemplate = Hogan.compile('<td><p class="{{class}}">{{{content}}}</p></td>\n');

      // apply the Read/Less only to Abstract and Authors fields
      var valueClasses = {
        abstract: 'readmore',
        authors: 'readmore',
      };

      var authorTemplate = Hogan.compile('{{author}}<br>');

      var authorsValue = '';
      if (dataModal.authors) {
        $.each(dataModal.authors, function(id, author) {
          authorsValue += authorTemplate.render({
            author: author.name
          });
        });
      }

      dataModal.authors = authorsValue;

      var tableContent = '';

      $.each(dataModal, function(id, value) {
        if ($.inArray(id, that.ignoredFields) !== -1) {
          return;
        }
        var labelCell = cellTemplate.render({
          class: 'cell-width',
          content: that.labels[id],
        });
        var valueCell = cellTemplate.render({
          class: valueClasses[id],
          content: value,
        });

        var row = rowTemplate.render({
          content: labelCell + valueCell
        });
        tableContent += row;

      });

      var table = tableTemplate.render({
        content: tableContent
      });

      // populate the body of the modal
      this.$table.html(table);

      // show the modal
      this.$element.modal({
        backdrop: 'static',
        keyboard: false
      });
    },

    connectEvents: function() {

      var that = this;

      this.$acceptButton.on('click', function(event) {
        that.$element.trigger('accepted');
      });

      this.$rejectButton.on('click', function(event) {
        that.$element.trigger('rejected');
      });

      this.$element.on('shown.bs.modal', function(e) {
        // trigger the More/Less on the Authors and Abstract fields
        $('.readmore').readmore({
          speed: 200,
          maxHeight: 80,
          moreLink: '<div class="pull-left"><a href="" class="fa fa-caret-square-o-down"' +
            'style="font-size: 12px;"> Show more</a></div>',
          lessLink: '<div class="pull-left"><a href="" class="fa fa-caret-square-o-up"' +
            'style="font-size: 12px;"> Show less</a></div>'
        });
      });
    }
  };
  module.exports = PreviewModal;
});
