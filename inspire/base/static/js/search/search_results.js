define(
  [
    'jquery',
    'flight/lib/component',
    'bootstrap'
  ],
  function($, defineComponent) {
    'use strict';

    var sList = [];

    return defineComponent(SearchResults);

    function SearchResults() {
      var minimum_page_limit = $("#results-per-page option:selected").text();
      this.attributes({
        EXPORT_LIMIT: 5000
      });

      this.get_download_information = function(type) {
        var obj = {
          filename: '',
          url: ''
        };
        switch (type) {
          case 'BibTex':
            obj['filename'] = 'bibtex.bib';
            obj['url'] = '/formatter/export-as/bibtex/';
            break;
          case 'LaTex(EU)':
            obj['filename'] = 'latex_eu.tex';
            obj['url'] = '/formatter/export-as/latex_eu/';
            break;
          case 'LaTex(US)':
            obj['filename'] = 'latex_us.tex';
            obj['url'] = '/formatter/export-as/latex_us/';
            break;
          case 'CV format (LaTex)':
            obj['filename'] = 'cv_format_latex.tex';
            obj['url'] = '/formatter/export-as/cv_latex/';
            break;
          case 'CV format (html)':
            obj['filename'] = 'cv_format_html.html';
            obj['url'] = '/formatter/export-as/cv_latex_html/';
            break;
          case 'CV format (text)':
            obj['filename'] = 'cv_format_text.txt';
            obj['url'] = '/formatter/export-as/cv_latex_text/';
            break;
          default:
            obj['filename'] = 'bibtex.bib';
            obj['url'] = '/formatter/export-as/bibtex/';
        }
        return obj;
      }

      this.onDownloadBibtex = function(ev) {
        $.getJSON('/formatter/bibtex', {
          recid: $(ev.target).data("recid")
        }, function(data) {
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('BibTex')
          $("#download" + data.recid).attr("href", "/formatter/download-bibtex/" + data.recid)
        });
      }

      this.onDownloadLatexEu = function(ev) {
        $.getJSON('/formatter/latex', {
          recid: $(ev.target).data("recid"),
          latex_format: 'latex_eu'
        }, function(data) {
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('LaTex(EU)')
          $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_eu/" + data.recid)
        });
      }

      this.onDownloadLatexUs = function(ev) {
        $.getJSON('/formatter/latex', {
          recid: $(ev.target).data("recid"),
          latex_format: 'latex_us'
        }, function(data) {
          $("#text" + data.recid).text(data.result);
          $("#format" + data.recid).text('LaTex(US)')
          $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_us/" + data.recid)
        });
      }

      this.initExportDropdown = function() {
        $('#formats-dropdown-menu > li').each(function(index) {
          $(this).on("click", function() {
            $("#dropdown-export").html($(this).text() + ' <span class="caret"></span>');
          });
        });
      }

      this.onChangeArrow = function(ev) {
        var split_id = $(ev.target).attr('id').split('-');
        var recid = split_id[split_id.length - 1];
        var $dots = $('#dots' + recid);
        var $id_down = $('#arrow_down-' + recid);
        var $id_up = $('#arrow_up-' + recid);
        if (split_id[0].match("^arrow_down")) {
          $dots.hide();
          $id_up.show();
          $id_down.hide();
        } else {
          $id_up.hide();
          $dots.show();
          $id_down.show();
        }
      }

      this.onExportSelectAll = function(ev) {
        var EXPORT_LIMIT = this.attr.EXPORT_LIMIT;
        var that = this;
        sList = [];
        if ($(ev.target).prop('checked')) {
          $('.checkbox-results').each(function() {
            $(this).prop('checked', true);
            sList.push($(this).attr("id"));
          });

          if (parseInt($('#total-results').text()) > minimum_page_limit) {
            if (parseInt($('#total-results').text()) > EXPORT_LIMIT) {
              $('#results-control-panel').after('<div class="panel panel-default" id="info-message">' +
                '<div class="panel-body" >You have selected ' + sList.length + ' records of this page. <a class="pointer" id="select-all-records">' +
                'Select ' + EXPORT_LIMIT + ' records (Maximum limit).</a></div></div>');
            } else {
              $('#results-control-panel').after('<div class="panel panel-default" id="info-message">' +
                '<div class="panel-body" >You have selected ' + sList.length + ' records of this page. <a class="pointer" id="select-all-records">' +
                'Select all ' + $('#total-results').text() + ' results.</a></div></div>');
            }
          } else {
            $('#results-control-panel').after('<div class="panel panel-default" id="info-message">' +
              '<div class="panel-body" >You have selected ' + sList.length + ' records of this page.</div></div>');
          }
          this.on('#select-all-records', "click", this.onSelectAllRecords);
        } else {
          $('.checkbox-results').each(function() {
            $(this).prop('checked', false);
          });
          sList = [];
          $('#info-message').remove();
          $('#alert-selection').remove();
        }
      }

      this.onSelectAllRecords = function(ev) {
        var that = this;
        var limit = $('#total-results').text();
        $('#info-message').remove();
        if (parseInt($('#total-results').text()) > this.attr.EXPORT_LIMIT) {
          limit = this.attr.EXPORT_LIMIT;
        }
        $.get("/search?of=id&rg=" + limit, function(data, status) {
          if (status == 'success') {
            $('#results-control-panel').after('<div class="alert alert-warning" id="alert-selection" role="alert">' +
              data.length + ' records have been selected.<a class="pointer" id="undo-selection"> Undo selection.</a></div>');
            $('#undo-selection').on("click", $.proxy(that.onUndoSelection, that));
            sList = data;
          }
        });
      }

      this.onUndoSelection = function(ev) {
        sList = [];
        $('#alert-selection').remove();
        $('.checkbox-results').each(function() {
          $(this).prop('checked', false);
        });
        $('#export-select-all').prop('checked', false);
        $('#export-select-all').prop('indeterminate', false);
      }

      this.onExportAs = function(ev) {
        var obj = this.get_download_information($('#dropdown-export').text().trim());
        if (sList.length != 0) {
          $('#spinner-download').show();
          $('#download-format').text('Downloading...');
          $('#download-format').addClass('disabled');
          $.ajax({
            type: "POST",
            url: obj['url'],
            data: {
              ids: sList
            },
            success: function(data) {
              var response_data = "text/plain;charset=utf-8," + encodeURIComponent(data);
              $("body").append('<a id="data-download" href="data:' + response_data + '" download="' + obj['filename'] + '">download</a>');
              var trigger_element = document.getElementById('data-download');
              trigger_element.click();
              $("#data-download").remove();
            }
          }).done(function() {
            $('#spinner-download').hide();
            $('#download-format').text('Download');
            $('#download-format').removeClass('disabled');
          });
        }
      }

      this.onCheckboxChange = function(ev) {
        var checkboxes = document.querySelectorAll('input.checkbox-results');
        var checkedCount = document.querySelectorAll('input.checkbox-results:checked').length;
        var checkall = document.getElementById('export-select-all');

        checkall.checked = checkedCount > 0;
        checkall.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
        if ($(ev.target).prop('checked')) {
          sList.push($(ev.target).attr("id"));
        } else {
          var index = sList.indexOf($(ev.target).attr("id"))
          if (index > -1) {
            sList.splice(index, 1);
          }
        }
        if (sList.length != 0) {
          $("#dropdown-export").html($('#dropdown-export').text().trim() + ' <span class="caret"></span>');
        }
      }

      this.onNumpagesChange = function(ev) {
        $('form[name=search] input[name=rg]').val($(ev.target).val());
        $('form[name=search]').submit();
      }

      this.onSortingChange = function(ev) {
        var $sortField = $('form[name=search] input[name=sf]'),
            $sortOrder = $('form[name=search] input[name=so]');
        var sortingVal = $("#select-sorting").val();
        switch (sortingVal) {
          case 'bestmatch':
            $sortField.val('');
            $sortOrder.val('');
            break;
          case 'newest':
            $sortField.val('earliest_date');
            $sortOrder.val('desc');
            break;
          case 'oldest':
            $sortField.val('earliest_date');
            $sortOrder.val('asc');
            break;
        }
        $('form[name=search]').submit();
      }

      this.onDropdownCheck = function() {
        $("#dropdown-export").dropdown("toggle");
      }

      this.after('initialize', function() {
        sList = [];
        $('[data-toggle="tooltip"]').tooltip()
        this.on("[id^=arrow]", "click", this.onChangeArrow);
        this.on(".dropdown-cite, .bibtex", "click", this.onDownloadBibtex);
        this.on(".latex_eu", "click", this.onDownloadLatexEu);
        this.on(".latex_us", "click", this.onDownloadLatexUs);
        this.on("#export-select-all", "click", this.onExportSelectAll);
        this.on("#checkbox-parent > input[type=checkbox]", "change", this.onCheckboxChange);
        this.on("#download-format", "click", this.onExportAs);
        this.on("#select-numpages", "change", this.onNumpagesChange);
        this.on("#select-sorting", "change", this.onSortingChange);
        this.initExportDropdown();
        this.on("a.export-as-element", "click", this.onDropdownCheck);
      });

    }

  });
