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
    'flight',
    'bootstrap',
    'clipboard'
  ],
  function($, flight, Bootstrap, Clipboard) {
    'use strict';

    return flight.component(CitationsModal);

    function CitationsModal() {
      this.onSelectContent = function(record_id) {
        setTimeout(function(){
            var id = 'singleRecord' + record_id
            var range = document.createRange();
            range.selectNodeContents(document.getElementById(id));
            var sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range); 
          }, 300);
      }

      this.onCiteClick = function(ev) {
        var that = this;
        $('.copy-clp').addClass('disabled');
        $('.copy-clp' + $(ev.target).data("recid")).tooltip();
        $.getJSON('/formatter/bibtex', {
          recid: $(ev.target).data("recid")
        }, function(data) {
          $('.copy-clp').removeClass('disabled');
          $('.copy-clp').tooltip('destroy');
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('BibTex')
          $("#download" + data.recid).attr("href", "/formatter/download-bibtex/" + data.recid)
          that.onSelectContent($(ev.target).data("recid"));
        })
      }

      this.onLatexEUClick = function(ev) {
        var that = this;
        $('.copy-clp').addClass('disabled');
        $('.copy-clp').tooltip();
        $.getJSON('/formatter/latex', {
          recid: $(ev.target).data("recid"),
          latex_format: 'latex_eu'
        }, function(data) {
          $('.copy-clp').removeClass('disabled');
          $('.copy-clp').tooltip('destroy');
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('LaTex(EU)')
          $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_eu/" + data.recid)
          that.onSelectContent($(ev.target).data("recid"));
        })
      }

      this.onLatexUSClick = function(ev) {
        var that = this;
        $('.copy-clp').addClass('disabled');
        $('.copy-clp').tooltip();
        $.getJSON('/formatter/latex', {
          recid: $(ev.target).data("recid"),
          latex_format: 'latex_us'
        }, function(data) {
          $('.copy-clp').removeClass('disabled');
          $('.copy-clp').tooltip('destroy');
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('LaTex(US)')
          $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_us/" + data.recid)
          that.onSelectContent($(ev.target).data("recid"));
        })
      }

      this.onCopyToClipboard = function(ev) {
        $('#' + $(ev.target).attr("id")).tooltip();        
        var clipboard = new Clipboard('#' + $(ev.target).attr("id"));
        clipboard.on('success', function(e) {
          $('#' + $(ev.target).attr("id")).attr('data-original-title','Copied!').tooltip('show');
        });
      }

      this.after('initialize', function() {
        $(".copy-clp").hover(function(){
          $(".copy-clp").tooltip('destroy');
        });
        this.on('.dropdown-cite, .bibtex', 'click', this.onCiteClick);
        this.on('.latex_eu', 'click', this.onLatexEUClick);
        this.on('.latex_us', 'click', this.onLatexUSClick);
        this.on(".copy-clp", "click", this.onCopyToClipboard);
      });
    }
  });