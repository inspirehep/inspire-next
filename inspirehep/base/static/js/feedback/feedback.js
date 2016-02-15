 /*
  * This file is part of INSPIRE.
  * Copyright (C) 2015, 2016 CERN.
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
   'hgn!js/feedback/templates/email',
   'hgn!js/feedback/templates/error',
   'hgn!js/feedback/templates/modal',
 ], function($, buttonTemplate, emailTemplate, errorTemplate, modalTemplate) {
   return {
     'Feedback': function(opts) {
       var options = {};

       this.initFeedback = function(opts) {
         options['button'] = opts['button'] || 'Send';
         options['close'] = opts['close'] || 'Close';
         options['emailError'] = opts['emailError'] ||
           '<strong>Oh snap!</strong> We need your email to follow up on your feedback.';
         options['emailLabel'] = opts['emailLabel'] ||
           'Please enter your email:';
         options['feedbackError'] = opts['feedbackError'] ||
           '<strong>Oh snap!</strong> It seems like you forgot to input your feedback?';
         options['feedbackLabel'] = opts['feedbackLabel'] ||
           'INSPIRE Labs welcomes problem reports, feature ideas and general comments:';
         options['feedbackClarification'] = opts['feedbackClarification'] ||
           'Please, do not use this form for inspirehep.net comments/corrections.';
         options['title'] = opts['title'] || 'Send Feedback';
         options['serverError'] = opts['serverError'] ||
           '<strong>Oh snap!</strong> Something bad has happened on our side.';
         options['url'] = opts['url'] || '/postfeedback';

         this.displayButton();
         this.displayModal();
         this.handleSubmit();
         this.handleClosing();
       };

       this.displayButton = function() {
         $('body').append(buttonTemplate({
           title: options['title']
         }));
       };

       this.displayModal = function() {
         $('body').append(modalTemplate({
           title: options['title'],
           button: options['button'],
           label: options['feedbackLabel'],
           clarification: options['feedbackClarification'],
           close: options['close'],
         }));
       };

       this.handleSubmit = function() {
         $('#feedbackModalForm').on('submit', function(event) {
           event.preventDefault();

          var $error = $(this).find('#feedbackModalError'),
            $feedback = $(this).find('#feedbackModalFeedback'),
            $email = $(this).find('#feedbackModalEmail'),
            $replytoaddr = $(this).find('#feedbackModalReplytoaddr'),
            $modal = $(this).closest('.modal');

           var feedback = $feedback.val(),
             replytoaddr = $replytoaddr.val();

           var data = 'feedback=' + feedback +
             ((replytoaddr) ? '&replytoaddr=' + replytoaddr : '');

           if (feedback.length) {
             $.ajax({
               type: 'POST',
               url: options['url'],
               data: data,
               statusCode: {
                 200: function () {
                   $feedback.val('');
                   $modal.modal('hide');
                 },
                 403: function () {
                   $email.html(emailTemplate({label: options['emailLabel']}));
                   $error.html(errorTemplate({error: options['emailError']}));
                 },
                 500: function () {
                   $error.html(errorTemplate({error: options['serverError']}));
                 }
               }
             });
           } else {
             $error.html(errorTemplate({error: options['feedbackError']}));
           }
         });
       };

       this.handleClosing = function() {
         $('#feedbackModal').on('hide.bs.modal', function(event) {
           $(this).find('#feedbackModalEmail').empty();
           $(this).find('#feedbackModalError').empty();
         });
       };

       this.initFeedback(opts);
     },
   };
 });
