require(['jquery', 'bootstrap'], function($) {

	$(function () {
	  $('[data-toggle="tooltip"]').tooltip()
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
		  
		$('#bibtex_text').show();
		$('#latex_text_eu').hide();
		$('#harvmac_text').hide();
		$('#endnote_text').hide();
		$('#latex_text_us').hide();

	$('#bibtex').click(function(){
		$('#bibtex_text').show();
		$('#latex_text_eu').hide();
		$('#harvmac_text').hide();
		$('#endnote_text').hide();
		$('#latex_text_us').hide();
		$('#btn-drop').text('Format: BibTex ')
		var newSpan = $('<span class="caret">')
		$('#btn-drop').append(newSpan);
	});

	$('#latex_us').click(function(){
		$('#bibtex_text').hide();
		$('#latex_text_eu').hide();
		$('#harvmac_text').hide();
		$('#endnote_text').hide();
		$('#latex_text_us').show();
		$('#btn-drop').text('Format: LaTex(US) ')
		var newSpan = $('<span class="caret">')
		$('#btn-drop').append(newSpan);
	});

	$('#latex_eu').click(function(){
		$('#bibtex_text').hide();
		$('#latex_text_eu').show();
		$('#harvmac_text').hide();
		$('#endnote_text').hide();
		$('#latex_text_us').hide();
		$('#btn-drop').text('Format: LaTex(EU) ')
		var newSpan = $('<span class="caret">')
		$('#btn-drop').append(newSpan);
	});

	$('#harvmac').click(function(){
		$('#bibtex_text').hide();
		$('#latex_text_eu').hide();
		$('#harvmac_text').show();
		$('#endnote_text').hide();
		$('#latex_text_us').hide();
		$('#btn-drop').text('Format: Harvmac ')
		var newSpan = $('<span class="caret">')
		$('#btn-drop').append(newSpan);
	});

	$('#endnote').click(function(){
		$('#bibtex_text').hide();
		$('#latex_text_eu').hide();
		$('#harvmac_text').hide();
		$('#endnote_text').show();
		$('#latex_text_us').hide();
		$('#btn-drop').text('Format: EndNote ')
		var newSpan = $('<span class="caret">')
		$('#btn-drop').append(newSpan);
	});
		
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

