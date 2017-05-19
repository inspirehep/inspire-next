define(function(require, exports, module) {
  "use strict";
  var $ = require("jquery");
  var tpl_field_message = require('hgn!js/forms/templates/field_message');

  function AuthorUpdateForm() {
    var $start_year_selector = $("input[id$='start_year']").not("input[id*='__index__']")
    var $end_year_selector = $("input[id$='end_year']").not("input[id*='__index__']")


   function initHandlers() {

    $('.add-element').click(refreshHandlers);

    $('.remove-element').click(refreshHandlers);

    $start_year_selector.each(function(index, el){
        el.addEventListener('change', start_year_init_listener);
    });

    $end_year_selector.each(function(index, el){
        el.addEventListener('change',end_year_init_listener);
    });
  }

  function resetSelectors() {
    $start_year_selector = $("input[id$='start_year']").not("input[id*='__index__']")
    $end_year_selector = $("input[id$='end_year']").not("input[id*='__index__']")
  }

  function removeHandlers() {
    $start_year_selector.each(function(index, el){
        el.removeEventListener('change', start_year_init_listener);
    });

    $end_year_selector.each(function(index, el){
        el.removeEventListener('change',end_year_init_listener);
    });
  }

  function refreshHandlers() {
      setTimeout(function() {
    removeHandlers();
    resetSelectors();
    initHandlers();
      }, 200)
  }

  function create_field_msg(field_message,field_name){
    var message = [field_message];
    var $state_name = $("#state-" + field_name);
    var $state_group_name = $("#state-group-" + field_name);
    $state_name.html(tpl_field_message({
      name: field_name,
      state: 'error',
      messages: message
    }));
    $state_group_name.addClass('error');
    $state_name.addClass('alert-danger');
    $state_name.show('fast');
  }


  function start_year_init_listener(event) {
    var elem = event.target;
    var elemValue = parseInt(elem.value, 10);
    var elemId = elem.id;
    var otherFieldId = elemId.replace('start_year', 'end_year');
    var otherFieldValue = parseInt(document.getElementById(otherFieldId).value, 10);
    if(otherFieldValue!== NaN && elemValue > otherFieldValue && elemValue!==NaN) {
      setTimeout(function() {
      create_field_msg('Start Year should be earlier than End Year', elemId)
    }, 200)
  }
  }

  function end_year_init_listener(event) {
    var elem = event.target;
    var elemValue = parseInt(elem.value, 10);
    var elemId = elem.id;
    var otherFieldId = elemId.replace('end_year', 'start_year');
    var otherFieldValue = parseInt(document.getElementById(otherFieldId).value, 10);
    var isNumber =  /^\d{4}$/.test(otherFieldValue);//check if the fields value is a compatible number
    var isNumber_other =  /^\d{4}$/.test(otherFieldValue);//check if the other fields value is a compatible number
    if(isNumber!== false && elemValue < otherFieldValue && isNumber_other!==false) {
      setTimeout(function() {
      create_field_msg('Start Year should be earlier than End Year', otherFieldId)
    }, 200)
    }
    else if(isNumber_other){//if it is a compatible number we delete the error
      $("#state-" + otherFieldId).hide();
    }
  }

    initHandlers();
  }


  module.exports = AuthorUpdateForm;
});
