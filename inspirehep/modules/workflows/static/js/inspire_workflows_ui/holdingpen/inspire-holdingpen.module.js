/**
 * Created by eamonnmaguire on 25/05/2016.
 */

(function (angular) {
  var invenioHoldingPen = angular.module("invenioHoldingPen", []);

  invenioHoldingPen.factory("HoldingPenDetailViewService", ["$http",
    function ($http) {
      return {
        getRecord: function (vm, workflowId) {
          $http.get('/api/holdingpen/' + workflowId).then(function (response) {
            vm.record = response.data;
          }).catch(function (value) {
            vm.record = {};
          });
        }
      }
    }]
  );


  function holdingPen() {

    var controller = ["$scope", "HoldingPenDetailViewService",
      function ($scope, HoldingPenDetailViewService) {

        $scope.vm = {};
        $scope.vm.loading = true;
        HoldingPenDetailViewService.getRecord($scope.vm, $scope.workflowId);

      }
    ];

    function templateUrl(element, attrs) {
      return attrs.template;
    }

    return {
      templateUrl: templateUrl,
      restrict: 'AE',
      scope: {
        workflowId: '@workflowId'
      },
      controller: controller
    };
  }

  invenioHoldingPen.directive("holdingPen", holdingPen);
})(angular);
