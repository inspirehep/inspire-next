/*
 ** This file is part of INSPIRE.
 ** Copyright (C) 2015 CERN.
 **
 ** INSPIRE is free software: you can redistribute it and/or modify
 ** it under the terms of the GNU General Public License as published by
 ** the Free Software Foundation, either version 3 of the License, or
 ** (at your option) any later version.
 **
 ** INSPIRE is distributed in the hope that it will be useful,
 ** but WITHOUT ANY WARRANTY; without even the implied warranty of
 ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 ** GNU General Public License for more details.
 **
 ** You should have received a copy of the GNU General Public License
 ** along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 **
 ** In applying this licence, CERN does not waive the privileges and immunities
 ** granted to it by virtue of its status as an Intergovernmental Organization
 ** or submit itself to any jurisdiction.
 */
 
define(
  [
    'jquery',
    'flight/lib/component',
    'bootstrap'
  ],
  function($, defineComponent) {
    'use strict';

    return defineComponent(CitationsModal);

    function CitationsModal() {

      this.onCiteClick = function(ev) {
        $.getJSON('/formatter/bibtex', {
          recid: $(ev.target).data("recid")
        }, function(data) {
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('BibTex')
          $("#download" + data.recid).attr("href", "/formatter/download-bibtex/" + data.recid)
        })
      }

      this.onLatexEUClick = function(ev) {
        $.getJSON('/formatter/latex', {
          recid: $(ev.target).data("recid"),
          latex_format: 'latex_eu'
        }, function(data) {
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('LaTex(EU)')
          $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_eu/" + data.recid)
        })
      }

      this.onLatexUSClick = function(ev) {
        $.getJSON('/formatter/latex', {
          recid: $(ev.target).data("recid"),
          latex_format: 'latex_us'
        }, function(data) {
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('LaTex(US)')
          $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_us/" + data.recid)
        })
      }

      this.onSelectContent = function(ev) {
        document.execCommand('selectAll', false, null);
        $(this).off(ev);
      }

      this.after('initialize', function() {
        this.on('.dropdown-cite, .bibtex', 'click', this.onCiteClick);
        this.on('.latex_eu', 'click', this.onLatexEUClick);
        this.on('.latex_us', 'click', this.onLatexUSClick);
        this.on('.editable', 'click', this.onSelectContent);
      });
    }
  });