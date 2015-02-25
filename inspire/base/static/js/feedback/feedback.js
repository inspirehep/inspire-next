 /*
 * This file is part of INSPIRE.
 * Copyright (C) 2015 CERN.
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
  'hgn!js/feedback/templates/button',
  'hgn!js/feedback/templates/error',
  'hgn!js/feedback/templates/modal',
], function ($, buttonTemplate, errorTemplate, modalTemplate) {
  return {
    'Feedback': function (opts) {
      var options = {};

      this.initFeedback = function (opts) {
        options['button'] = opts['button'] || 'Send';
        options['close'] = opts['close'] || 'Close';
        options['error'] = opts['error'] ||
          '<strong>Oh snap!</strong> It seems like you forgot to input your feedback?';
        options['label'] = opts['label'] ||
          'We welcome problem reports, feature ideas and general comments:';
        options['title'] = opts['title'] || 'Send Feedback';
        options['url'] = opts['url'] || '/postfeedback';

        this.displayButton();
        this.displayModal();
        this.handleSubmit();
        this.handleClosing();
      };

      this.displayButton = function () {
        $('body').append(buttonTemplate({
          title: options['title']
        }));
      };

      this.displayModal = function () {
        $('body').append(modalTemplate({
          title: options['title'],
          button: options['button'],
          label: options['label'],
          close: options['close'],
        }));
      };

      this.handleSubmit = function () {
        $('#feedbackModalForm').on('submit', function (event) {
          event.preventDefault();

          var $errors = $(this).find('#feedbackModalErrors'),
              $body = $(this).find('#feedbackModalBody'),
              $modal = $(this).closest('.modal');

          var feedback = $body.val();
          if (feedback.length) {
            $.ajax({
              data: 'data=' + encodeURIComponent(JSON.stringify(feedback)),
              headers: {
                "Content-type": "application/x-www-form-urlencoded",
              },
              type: 'POST',
              url: options['url'],
            });

            $errors.empty();
            $body.val('');
            $modal.modal('hide');
          } else {
            $errors.html(errorTemplate({
              error: options['error'],
            }));
          }
        });
      };

      this.handleClosing = function () {
        $('#feedbackModal').on('hide.bs.modal', function (event) {
          $(this).find('#feedbackModalErrors').empty();
        });
      };

      this.initFeedback(opts);
    },
  };
});
