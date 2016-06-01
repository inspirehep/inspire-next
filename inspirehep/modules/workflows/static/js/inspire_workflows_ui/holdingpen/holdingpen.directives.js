/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
 *
 * INSPIRE is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 *
 * In applying this license, CERN does not
 * waive the privileges and immunities granted to it by virtue of its status
 * as an Intergovernmental Organization or submit itself to any jurisdiction.
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
