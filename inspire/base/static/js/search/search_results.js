require(['jquery', 'bootstrap'], function($) {

  $(function () {
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

  $( document ).ready(function() {
    var loc = window.location.href;
    var is_root = location.pathname == "/";
    if(/references/.test(loc)) {
      $('.information').removeClass('active');
      $('.references').addClass('active');
    }

    if(/citations/.test(loc)) {
      $('.information').removeClass('active');
      $('.citations').addClass('active');
    }

    if(/plots/.test(loc)) {
      $('.information').removeClass('active');
      $('.plots').addClass('active');
    }
  
    if(is_root) {
      $('#search-box-main').addClass('search-box-centered');
    }
  
  });

  $(".fa-arrow-up").hide();
  functions = {
    changeArrow: function(id,id_down,id_up) {
      var dots = $('#dots'+id);
      var id_down = $('#'+id_down);
      var id_up = $('#'+id_up); 
      if(id_up.css('display')=='none') {
        dots.hide();
        id_up.show();
        id_down.hide();
      }
      else {
        id_up.hide();
        dots.show();
        id_down.show();
      }       
    }     
  }

});
