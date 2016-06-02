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
            HoldingPenRecordService.setBatchDecision(
              $scope.vm.invenioSearchResults.hits.hits,
              $scope.vm.selected_records,
              decision)
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
            HoldingPenRecordService.setDecision($scope.record._source,
              $scope.record._id, decision)
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

  function holdingPenDashboardItem() {

    var controller = ["$scope", "$http",
      function ($scope, $http) {
        $http.get('/api/holdingpen/?' + $scope.primaryFilterKey + '=' + $scope.primaryFilterValue)
          .then(function (response) {
            $scope.vm = $scope;
            $scope.vm.total = response.data.hits.total;
            $scope.vm.secondary_filters = {
              'WAITING': 0,
              'ERROR': 0,
              'HALTED': 0,
              'COMPLETED': 0
            };

            for (var bucket_idx in response.data.aggregations[$scope.secondaryFilter].buckets) {
              var bucket = response.data.aggregations[$scope.secondaryFilter].buckets[bucket_idx];
              $scope.vm.secondary_filters[bucket.key] = +bucket.doc_count;
            }

            $scope.vm.class_name = $scope.primaryFilterValue.toLowerCase().replace(" ", "-")

          }).catch(function (value) {
          console.error("Problem occurred when getting " + $scope.primary_filter_key);
        });
      }
    ];

    function templateUrl(element, attrs) {
      return attrs.template;
    }

    return {
      templateUrl: templateUrl,
      restrict: 'AE',
      scope: {
        sectionTitle: '@sectionTitle',
        primaryFilterKey: '@primaryFilterKey',
        primaryFilterValue: '@primaryFilterValue',
        secondaryFilter: '@secondaryFilter'
      },
      controller: controller
    };
  }

  angular.module('holdingpen.directives', [])
    .directive('holdingPenDecision', holdingPenDecision)
    .directive('holdingPen', holdingPenDetail)
    .directive('holdingPenBatchDecision', holdingPenBatchDecision)
    .directive('holdingPenDashboardItem', holdingPenDashboardItem);

})(angular);
