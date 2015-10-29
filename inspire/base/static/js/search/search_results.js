require(['jquery', 'bootstrap'], function($) {

  $(function() {
    $('[data-toggle="tooltip"]').tooltip()

    $(".dropdown-cite").on('click', function() {
      $.getJSON('/formatter/bibtex', {
        recid: $(this).data("recid")
      }, function(data) {
        $("#text" + data.recid).text(data.result);
        $("#format" + data.recid).text('BibTex')
        $("#download" + data.recid).attr("href", "/formatter/download-bibtex/" + data.recid)
      });
    });

    $(".bibtex").on('click', function() {
      $.getJSON('/formatter/bibtex', {
        recid: $(this).data("recid")
      }, function(data) {
        $("#text" + data.recid).text(data.result);
        $("#format" + data.recid).text('BibTex')
        $("#download" + data.recid).attr("href", "/formatter/download-bibtex/" + data.recid)
      });
    });

    $(".latex_eu").on('click', function() {
      $.getJSON('/formatter/latex', {
        recid: $(this).data("recid"),
        latex_format: 'latex_eu'
      }, function(data) {
        $("#text" + data.recid).text(data.result);
        $("#format" + data.recid).text('LaTex(EU)')
        $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_eu/" + data.recid)
      });
    });

    $(".latex_us").on('click', function() {
      $.getJSON('/formatter/latex', {
        recid: $(this).data("recid"),
        latex_format: 'latex_us'
      }, function(data) {
        $("#text" + data.recid).text(data.result);
        $("#format" + data.recid).text('LaTex(US)')
        $("#download" + data.recid).attr("href", "/formatter/download-latex/latex_us/" + data.recid)
      });
    });

  })

  $('#formats-dropdown-menu > li').each(function(index) {
    $(this).on("click", function() {
      $("#dropdown-export").html($(this).text() + ' <span class="caret"></span>');
    });
  });

  var sList = [];
  var EXPORT_LIMIT = 5000;
  $('#checkbox-select-all').click(function(event) {
    sList = [];
    if (this.checked) {
      $('.checkbox-results').each(function() {
        this.checked = true;
        sList.push($(this).attr("id"));
      });

      if (parseInt($('#total-results').text()) > EXPORT_LIMIT) {
        $('#results-panel').after('<div class="panel panel-default" id="info-message">' +
          '<div class="panel-body" >You have selected ' + sList.length + ' records of this page. <a class="pointer" id="select-all-records">' +
          'Select ' + EXPORT_LIMIT + ' records (Maximum limit).</a></div></div>');
      } else {
        $('#results-panel').after('<div class="panel panel-default" id="info-message">' +
          '<div class="panel-body" >You have selected ' + sList.length + ' records of this page. <a class="pointer" id="select-all-records">' +
          'Select all ' + $('#total-results').text() + ' results.</a></div></div>');
      }

      $('#select-all-records').on('click', function() {
        $('#info-message').remove();
        $.get("/search?of=id&rg=" + EXPORT_LIMIT, function(data, status) {
          if (status == 'success') {
            $('#results-panel').after('<div class="alert alert-warning" id="alert-selection" role="alert">' +
              data.length + ' records have been selected.<a class="pointer" id="undo-selection"> Undo selection.</a></div>');
            sList = data;
          }
        });
      });
    } else {
      $('.checkbox-results').each(function() {
        this.checked = false;
      });
      sList = [];
      $('#info-message').remove();
      $('#alert-selection').remove();
    }
  });

  $(document).on('click', '#undo-selection', function(e) {
    sList = [];
    $('#alert-selection').remove();
    $('.checkbox-results').each(function() {
      this.checked = false;
    });
    $('#checkbox-select-all').prop('checked', false);
  });


  $('#checkbox-parent > input[type=checkbox]').change(function() {
    var $this = $(this);
    if (this.checked) {
      sList.push($this.attr("id"));
    } else {
      var index = sList.indexOf($this.attr("id"))
      if (index > -1) {
        sList.splice(index, 1);
      }
    }
    if (sList != 0) {
      $("#dropdown-export").html($('#dropdown-export').text().trim() + ' <span class="caret"></span>');
    }
  });

  var $loading = $('#spinner-download').hide();
  $("#download-format").on('click', function() {
    var obj = get_download_information($('#dropdown-export').text().trim());
    if (sList.length != 0) {
      $loading.show();
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
          $("body").append('<a id="data-download" href="data:' + response_data + '" download="export_as.' +
            obj['format'] + '">download</a>');
          var trigger_element = document.getElementById('data-download');
          trigger_element.click();
          $("#data-download").remove();
        }
      }).done(function() {
        $loading.hide();
        $('#download-format').text('Download');
        $('#download-format').removeClass('disabled');
      });
    }
  });

  function get_download_information(type) {
    var obj = {
      format: '',
      url: ''
    };
    switch (type) {
      case 'BibTex':
        obj['format'] = 'bibtex';
        obj['url'] = '/formatter/export-as/bibtex/';
        break;
      case 'LaTex(EU)':
        obj['format'] = 'tex';
        obj['url'] = '/formatter/export-as/latex_eu/';
        break;
      case 'LaTex(US)':
        obj['format'] = 'tex';
        obj['url'] = '/formatter/export-as/latex_us/';
        break;
      case 'CV format (LaTex)':
        obj['format'] = 'tex';
        obj['url'] = '/formatter/export-as/cv_latex/';
        break;
      case 'CV format (html)':
        obj['format'] = 'html';
        obj['url'] = '/formatter/export-as/cv_latex_html/';
        break;
      case 'CV format (text)':
        obj['format'] = 'txt';
        obj['url'] = '/formatter/export-as/cv_latex_text/';
        break;
      default:
        obj['format'] = 'bibtex';
        obj['url'] = '/formatter/export-as/bibtex/';
    }
    return obj;
  }

  $(".fa-arrow-up").hide();
  functions = {
    changeArrow: function(id, id_down, id_up) {
      var dots = $('#dots' + id);
      var id_down = $('#' + id_down);
      var id_up = $('#' + id_up);
      if (id_up.css('display') == 'none') {
        dots.hide();
        id_up.show();
        id_down.hide();
      } else {
        id_up.hide();
        dots.show();
        id_down.show();
      }
    }
  }

});
