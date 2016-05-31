/**
 * Created by eamonnmaguire on 25/05/2016.
 */

(function (angular) {
  var invenioHoldingPen = angular.module("invenioHoldingPen", []);

  /**
   * HoldingPenRecordService allows for the update of a record server
   * side through a post of the record JSON.
   */
  invenioHoldingPen.factory("HoldingPenRecordService", ["$http",
    function ($http) {
      return {
        /**
         * getRecord
         * @param vm
         * @param workflowId
         */
        getRecord: function (vm, workflowId) {
          $http.get('/api/holdingpen/' + workflowId).then(function (response) {
            vm.record = response.data;
            $('#breadcrumb').html(vm.record.metadata.breadcrumb_title);
          }).catch(function (value) {
            vm.ingestion_complete = false;
            alert(value);
          });
        },

        updateRecord: function (vm, workflowId) {
          $http.post('/api/holdingpen/' + workflowId + '/action/edit', vm.record).then(function (response) {
            vm.ingestion_complete = true;
          }).catch(function (value) {
            vm.ingestion_complete = false;
            alert(value);
          });
        },

        setDecision: function (vm, workflowId, decision) {
          var data = JSON.stringify({
            'value': decision
          });
          $http.post('/api/holdingpen/' + workflowId + '/action/resolve', data).then(function (response) {
            vm.ingestion_complete = true;
            vm.record._extra_data.user_action = decision;

          }).catch(function (value) {
            vm.error = value;
          });
        },

        deleteRecord: function (vm, workflowId) {
          $http.delete('/api/holdingpen/' + workflowId, vm.record).then(function (response) {
            vm.ingestion_complete = true;
          }).catch(function (value) {
            alert(value);
            vm.ingestion_complete = false;
          });
        },

        resumeWorkflow: function (vm, workflowId) {
          $http.post('/api/holdingpen/' + workflowId + '/action/resume').then(function (response) {
            vm.ingestion_complete = true;
          }).catch(function (value) {
            alert(value);
            vm.ingestion_complete = false;
          });
        },

        restartWorkflow: function (vm, workflowId) {
          $http.post('/api/holdingpen/' + workflowId + '/action/restart').then(function (response) {
            vm.ingestion_complete = true;
          }).catch(function (value) {
            alert(value);
            vm.ingestion_complete = false;
          });
        }


      }
    }]
  );


  function holdingPen() {

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

  invenioHoldingPen.directive("holdingPen", holdingPen);
})(angular);
