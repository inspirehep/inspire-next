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

  // require the Readmore library
  require("/vendors/readmore/readmore.min.js");

  //TODO: fill the form only when the user accepts the data

  // FIXME: move it inside the ModalPreview definition
  var o = $({});
  $.subscribe = o.on.bind(o);
  $.publish = o.trigger.bind(o);

  var s,
    ModalPreview = {

      settings: {
        myModal: $('#myModal'),
        button_import: $('#importData'),
        skip_import: $('#skipImportData'),
        //FIXME: find a better CSS selector
        // use jquery children, parents etc so don't break the behavior if html changes or classes
        hide_elements: $('#webdeposit_form_accordion > .panel:not(:first-child), #webdeposit_form_accordion + .well')
      },

      init: function(results) {
        s = this.settings;
        //console.log(s.myModal.find('.modal-body'));
        this.bindUIActions();
        this.renderModal(results);
      },

      renderModal: function(jsonData) {

        console.log(jsonData);

        //FIXME: better format the structure
        var tableTemplate = Hogan.compile('<table class="table table-stripped"><tr><th>Labels</th><th>Values</th></tr><tbody>{{{content}}}</tbody></table>');
        var rowTemplate = Hogan.compile('<tr>{{{content}}}</tr>\n');
        var cellTemplate = Hogan.compile('<td class="{{class}}">{{{content}}}</td>\n');

        var valueClasses = {
          abstract: 'readmore',
          contributors: 'readmore',
        };

        var authorTemplate = Hogan.compile('{{author}}<br>');

        var authorsValue = '';
        $.each(jsonData.contributors, function(index, author) {
          authorsValue += authorTemplate.render({
            author: author.name
          });
        });

        jsonData.contributors = authorsValue;

        var tableContent = '';

        $.each(jsonData, function(index, user) {
          var labelCell = cellTemplate.render({
            class: '',
            content: index,
          });
          var valueCell = cellTemplate.render({
            class: valueClasses[index],
            content: user,
          });

          var row = rowTemplate.render({
            content: labelCell + valueCell
          });
          tableContent += row;

          $.publish('validation/results');
        });

        var table = tableTemplate.render({
          content: tableContent
        });

        $('#myModal .modal-body').html(table);

        //FIXME: doesn't append More/Less
        $('.readmore').readmore({
          speed: 200,
          maxHeight: 90,
          moreLink: '<a href="#">Read more</a>',
          lessLink: '<a href="#">Less</a>'
        });

        //FIXME: fill the form only when the user accepts the data
        // var that = this;
        // $('#success').on('click', function(){
        //   that.fillForm(jsonData);
        // });

      },

      // smooth scrolling to the first box under the main one of the import
      scrollSmooth: function(el) {
        var $root = $('html, body');

        //FIXME: use selectors with jQuery and not CSS like children, parents etc.
        $('#webdeposit_form_accordion > .panel:not(:first-child), #webdeposit_form_accordion + .well').removeClass('hide');

        //FIXME: remove the hask from the url
        //FIXME: fix the smoothness, hangs when scrolling
        var href = $.attr(el, 'href');
        $root.animate({
          scrollTop: $(href).offset().top
        }, 500, function() {
          window.location.hash = '';
        });

      },

      bindUIActions: function() {

        console.log('bindUIActions');

        var that = this;

        s.button_import.on('click', function(e) {
          e.preventDefault();
          console.log('show modal');
          $.subscribe('validation/results', function(e) {
            // console.log(results); // print the results from the call when the AJAX is done
            s.myModal.modal();
          });
        });

        s.skip_import.on('click', function(e) {
          console.log('clicked');
          s.hide_elements.removeClass('hide');

          //var target = $('#webdeposit_form_accordion > .panel:eq(1)').children('.panel-collapse').attr('id');

          that.scrollSmooth(this);

        });

      }

    };

  module.exports = ModalPreview;
});
