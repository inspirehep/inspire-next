define(function (require, exports, module) {

  "use strict";

  var $ = require("jquery");
  var tpl_field_message = require('hgn!js/forms/templates/field_message');

  function AuthorUpdateForm() {

    this.$inspireForm = $('#authorUpdateForm');
    this.init();
  };

  AuthorUpdateForm.prototype = {
    init: function init() {
      var that = this;
      $('.add-element').click(function () {
        setTimeout(that.attachHandlers.bind(that), 200);
      });
      this.attachHandlers();
    },

    attachHandlers: function attachHandlers() {
      var that = this;
      var $yearSelector = $("input[id$='start_year'], input[id$='end_year']").not("input[id*='__index__']");
      
      $yearSelector.change(function(event) {
        that.onYearChange(event);
      });
    },

    onYearChange: function onYearChange(event) {
      var that = this;
      var elem = event.target;
      var elemValue = parseInt(elem.value, 10);
      var elemId = elem.id;
      var elemIdSplit = elemId.split('-');
      var otherFieldId = '';
      var otherFieldValue;
      var compareValues = false;
      
      if ( elemIdSplit[elemIdSplit.length - 1] === 'start_year' ) {
        otherFieldId = elemId.replace('start_year', 'end_year');
        otherFieldValue = parseInt(document.getElementById(otherFieldId).value, 10);
        compareValues = elemValue <= otherFieldValue;
      } else {
        otherFieldId = elemId.replace('end_year', 'start_year');
        otherFieldValue = parseInt(document.getElementById(otherFieldId).value, 10);
        compareValues = elemValue >= otherFieldValue;
      }

      var isNumber =  /^\d{4}$/.test(elemValue);
      var isOtherNumber =  /^\d{4}$/.test(otherFieldValue);

      if ( !isNumber || !isOtherNumber ) {
        return;
      }

      if ( !compareValues ) {
        setTimeout(function () {
          that.$inspireForm.trigger("handleFieldMessage", {
            name: elemId,
            data: {
              state: 'error',
              messages: ['Start Year should be earlier than End Year']
            }
          });
        }, 200);
      }
    }
  };

  module.exports = AuthorUpdateForm;
});
