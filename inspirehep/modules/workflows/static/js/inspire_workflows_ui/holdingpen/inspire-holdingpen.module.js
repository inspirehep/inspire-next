/**
 * Created by eamonnmaguire on 25/05/2016.
 */

(function (angular) {
  var inspireHoldingPen = angular.module("inspirehepHoldingPen", []);

  inspireHoldingPen.controller("holdingPenCtrl", function ($scope) {

  });

  inspireHoldingPen.directive("holding-pen", function () {
    return {
      template: "<h1>Made by a directive!</h1>"
    };
  });
})(angular);
