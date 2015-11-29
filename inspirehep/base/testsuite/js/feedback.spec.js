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
  'feedback',
  'bootstrap',
  'jasmine-ajax',
  'jasmine-jquery',
], function (Feedback) {
  'use strict';

  describe('Feedback', function () {
    var $backdrop,
        $body,
        $button,
        $close,
        $errors,
        $modal,
        $submit,
        feedback;

    beforeEach(function () {
      feedback = Feedback.Feedback({});

      $backdrop = $('.modal-backdrop');
      $button = $('.feedback-btn');
      $modal = $('#feedbackModal');

      $body = $modal.find('#feedbackModalBody');
      $close = $modal.find('.close');
      $errors = $modal.find('#feedbackModalErrors');
      $submit = $modal.find('[type=submit]');
    });

    afterEach(function () {
      $backdrop.remove();
      $button.remove();
      $modal.remove();
    });

    describe('init', function () {
      it('adds a single button to the page', function () {
        expect($button).toHaveLength(1);
      });

      it('adds a single modal to the page', function () {
        expect($modal).toHaveLength(1);
      });
    });

    describe('modal', function () {
      beforeEach(function () {
        $button.trigger('click');
      });

      afterEach(function () {
        $modal.hide();
      });

      it('is shown when clicking on the button', function () {
        expect($modal).toBeVisible();
      });

      it('is hidden when clicking on the close button', function () {
        $close.trigger('click');

        expect($modal).toBeHidden();
      });
    });

    describe('submit', function () {
      beforeEach(function () {
        $button.trigger('click');
      });

      it('accepts a filled submission', function () {
        jasmine.Ajax.withMock(function () {
          $.when(
            $body.val('foo'),
            $submit.trigger('click')
          ).then(function () {
            expect(jasmine.Ajax.requests.mostRecent().params)
              .toBe('data=%22foo%22');

            expect($errors).toBeEmpty();
            expect($modal).toBeHidden();
          });
        });
      });

      it('rejects an empty submission', function () {
        jasmine.Ajax.withMock(function () {
          $.when(
            $submit.trigger('click')
          ).then(function () {
            expect(jasmine.Ajax.requests.mostRecent()).toBeUndefined();

            expect($errors).toBeVisible();
            expect($modal).toBeVisible();
          });
        });
      });

      it('clears the errors when closed', function () {
        $submit.trigger('click');
        $close.trigger('click');

        expect($errors).toBeEmpty();
        expect($modal).toBeHidden();
      });
    });
  });
});
