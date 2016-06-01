/**
 * Created by eamonnmaguire on 01/06/2016.
 */

(function (angular) {

  function holdingPenBatchDecision() {

    var controller = ["$scope", "HoldingPenRecordService",
      function ($scope, HoldingPenRecordService) {

        $scope.BatchUtils = {
          setDecision: function (decision) {
            HoldingPenRecordService.setBatchDecision($scope.vm.selected_records, decision)
          }
        }
      }
    ];

    function templateUrl(element, attrs) {
      return attrs.template;
    }

    return {
      templateUrl: templateUrl,
      restrict: 'AE',
      scope: false,
      controller: controller
    };
  }

  function holdingPenDecision() {

    var controller = ["$scope", "HoldingPenRecordService",
      function ($scope, HoldingPenRecordService) {
        $scope.Utils = {
          setDecision: function (decision) {
            HoldingPenRecordService.setDecision($scope.record._source, $scope.record._id, decision)
          }
        }
      }
    ];

    function templateUrl(element, attrs) {
      return attrs.template;
    }

    return {
      templateUrl: templateUrl,
      restrict: 'AE',
      scope: {
        record: '=record'
      },
      controller: controller
    };
  }

  function holdingPenDetail() {

    var controller = ["$scope", "HoldingPenRecordService",
      function ($scope, HoldingPenRecordService) {
        $scope.vm = {};
        $scope.vm.loading = true;

        HoldingPenRecordService.getRecord($scope.vm, $scope.workflowId);

        $scope.Utils = {
          keys: function (obj) {
            if (obj != null)
              return Object.keys(obj);
            return [];
          },

          updateRecord: function () {
            HoldingPenRecordService.updateRecord($scope.vm, $scope.workflowId)
          },

          setDecision: function (decision) {
            HoldingPenRecordService.setDecision($scope.vm, $scope.workflowId, decision)
          },

          deleteRecord: function () {
            HoldingPenRecordService.deleteRecord($scope.vm, $scope.workflowId)
          },

          showHistory: function (url) {
            alert('Showing history');
          },

          registerUpdateEvent: function () {
            $scope.vm.update_ready = true;
            $scope.vm.saved = false;
            $scope.$emit();
          },

          resumeWorkflow: function () {
            HoldingPenRecordService.resumeWorkflow($scope.vm, $scope.workflowId)
          },

          restartWorkflow: function () {
            HoldingPenRecordService.restartWorkflow($scope.vm, $scope.workflowId)
          }
        }
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

  angular.module('holdingpen.directives', [])
    .directive('holdingPenDecision', holdingPenDecision)
    .directive('holdingPen', holdingPenDetail)
    .directive('holdingPenBatchDecision', holdingPenBatchDecision);

})(angular);
