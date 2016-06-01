/**
 * Created by eamonnmaguire on 25/05/2016.
 */

(function (angular) {

  var invenioHoldingPen = angular.module("invenioHoldingPen", ['xeditable',
    'holdingpen.services',
    'holdingpen.directives',
    'holdingpen.controllers',
    'holdingpen.filters.abstract']);

  invenioHoldingPen.run(function (editableOptions, editableThemes) {
    editableThemes.bs3.inputClass = 'input-md';
    editableThemes.bs3.buttonsClass = 'btn-md';
    editableOptions.theme = 'bs3';
  });
  /**
   * HoldingPenRecordService allows for the update of a record server
   * side through a post of the record JSON.
   */


})(angular);
