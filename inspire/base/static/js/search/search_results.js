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

  $("#export-as-bibtex").on('click', function() {
    if (sList != 0) {
      create_url('/formatter/export-as/bibtex/', sList);
    } else {
      $("#download").removeAttr('href');
    }
    $("#dropdown-export").html('BibTex <span class="caret"></span>');
  });

  $("#export-as-latex-eu").on('click', function() {
    if (sList != 0) {
      create_url('/formatter/export-as/latex_eu/', sList);
    } else {
      $("#download").removeAttr('href');
    }
    $("#dropdown-export").html('LaTex(EU) <span class="caret"></span>');
  });

  $("#export-as-latex-us").on('click', function() {
    if (sList != 0) {
      create_url('/formatter/export-as/latex_us/', sList);
    } else {
      $("#download").removeAttr('href');
    }
    $("#dropdown-export").html('LaTex(US) <span class="caret"></span>');
  });

  $("#export-as-cv-latex").on('click', function() {
    if (sList != 0) {
      create_url('/formatter/export-as/cv_latex/', sList);
    } else {
      $("#download").removeAttr('href');
    }
    $("#dropdown-export").html('CV format (LaTex) <span class="caret"></span>');
  });

  $("#export-as-cv-html").on('click', function() {
    if (sList != 0) {
      create_url('/formatter/export-as/cv_latex_html/', sList);
    } else {
      $("#download").removeAttr('href');
    }
    $("#dropdown-export").html('CV format (html) <span class="caret"></span>');
  });

  $("#export-as-cv-text").on('click', function() {
    if (sList != 0) {
      create_url('/formatter/export-as/cv_latex_text/', sList);
    } else {
      $("#download").removeAttr('href');
    }
    $("#dropdown-export").html('CV format (text) <span class="caret"></span>');
  });

  var sList = [];
  $('#checkbox-select-all').click(function(event) {
    if (this.checked) {
      $('.checkbox-results').each(function() {
        this.checked = true;
        sList.push($(this).attr("id"));
      });
      $('#results-panel').after('<div class="panel panel-default" id="info-message">' +
        '<div class="panel-body" >You have selected ' + sList.length + ' records of this page. <a class="pointer" id="select-all-records">' +
        'Select all ' + $('#total-results').text() + ' results.</a></div></div>');
      $('#select-all-records').on('click', function() {
        $('#info-message').remove();
        $('#results-panel').after('<div class="alert alert-warning" id="alert-selection" role="alert">' +
          $('#total-results').text() + ' have been selected.<a class="pointer" id="undo-selection"> Undo selection.</a></div>');
        $.get("/search?of=id&rg=" + $('#total-results').text(), function(data, status) {
          if (status == 'success') {
            sList = data;
            create_url(getType(), sList);
          } else {
            sList = [];
            $('#alert-selection').remove();
            $("#download").removeAttr('href');
            $('#results-panel').after('<div class="alert alert-danger" id="danger-selection" role="alert">' +
              'Too many records to download.</div>')
          }
        });
      });
    } else {
      $('.checkbox-results').each(function() {
        this.checked = false;
      });
      sList = [];
      $("#download").removeAttr('href');
      $('#info-message').remove();
      $('#alert-selection').remove();
    }
  });

  $(document).on('click', '#undo-selection', function(e) {
    sList = [];
    $('#alert-selection').remove();
    $("#download").removeAttr('href');
    $('.checkbox-results').each(function() {
      this.checked = false;
    });
    $('#checkbox-select-all').prop('checked', false);
  });

  function querystring(key) {
    var re = new RegExp('(?:\\?|&)' + key + '=(.*?)(?=&|$)', 'gi');
    var r = [],
      m;
    while ((m = re.exec(document.location.search)) != null) r.push(m[1]);
    return r;
  }

  $('input[type=checkbox]').change(function() {
    var $this = $(this);
    if (this.checked) {
      if ($this.attr("id") != 'checkbox-select-all') {
        sList.push($this.attr("id"));
      }
    } else {
      var index = sList.indexOf($this.attr("id"))
      if (index > -1) {
        sList.splice(index, 1);
      }
    }
    if ($('#dropdown-export').text().trim() == 'BibTex') {
      if (sList != 0) {
        create_url('/formatter/export-as/bibtex/', sList);
      } else {
        $("#download").removeAttr('href');
      }
      $("#dropdown-export").html('BibTex <span class="caret"></span>');
    } else if ($('#dropdown-export').text().trim() == 'LaTex(EU)') {
      if (sList != 0) {
        create_url('/formatter/export-as/latex_eu/', sList);
      } else {
        $("#download").removeAttr('href');
      }
      $("#dropdown-export").html('LaTex(EU) <span class="caret"></span>');
    } else if ($('#dropdown-export').text().trim() == 'LaTex(US)') {
      if (sList != 0) {
        create_url('/formatter/export-as/latex_us/', sList);
      } else {
        $("#download").removeAttr('href');
      }
      $("#dropdown-export").html('LaTex(US) <span class="caret"></span>');
    } else if ($('#dropdown-export').text().trim() == 'CV format (LaTex)') {
      if (sList != 0) {
        create_url('/formatter/export-as/cv_latex/', sList);
      } else {
        $("#download").removeAttr('href');
      }
      $("#dropdown-export").html('CV format (LaTex) <span class="caret"></span>');
    } else if ($('#dropdown-export').text().trim() == 'CV format (html)') {
      if (sList != 0) {
        create_url('/formatter/export-as/cv_latex_html/', sList);
      } else {
        $("#download").removeAttr('href');
      }
      $("#dropdown-export").html('CV format (html) <span class="caret"></span>');
    } else if ($('#dropdown-export').text().trim() == 'CV format (text)') {
      if (sList != 0) {
        create_url('/formatter/export-as/cv_latex_text/', sList);
      } else {
        $("#download").removeAttr('href');
      }
      $("#dropdown-export").html('CV format (text) <span class="caret"></span>');
    }
  });

  function getType() {
    url = ''
    switch ($('#dropdown-export').text().trim()) {
      case 'BibTex':
        url = '/formatter/export-as/bibtex/';
        break;
      case 'LaTex(EU)':
        url = '/formatter/export-as/latex_eu/';
        break;
      case 'LaTex(US)':
        url = '/formatter/export-as/latex_us/';
        break;
      case 'CV format (LaTex)':
        url = '/formatter/export-as/cv_latex/';
        break;
      case 'CV format (html)':
        url = '/formatter/export-as/cv_latex_html/';
        break;
      case 'CV format (text)':
        url = '/formatter/export-as/cv_latex_text/';
        break;
    }
    return url;
  }

  function create_url(url, sList) {
    var uniqueIds = [];
    $.each(sList, function(i, el) {
      if ($.inArray(el, uniqueIds) === -1) {
        uniqueIds.push(el);
      }
    });
    for (var i = 0; i < uniqueIds.length; i++) {
      url += uniqueIds[i] + ',';
    }
    clean_url = url.replace(/,\s*$/, "");
    $("#download").attr("href", clean_url);
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
