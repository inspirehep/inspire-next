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

  function holdingPenDetail() {

    var controller = ["$scope", "HoldingPenRecordService",
      function ($scope, HoldingPenRecordService) {
        $scope.vm = {};
        $scope.vm.loading = true;
        $scope.vm.new_subject_area = '';
        $scope.vm.new_keyword = '';

        $scope.vm.names = ["Theory-HEP", "Gravitation and Cosmology", "Astrophysics", "Math and Math Physics",
        "Phenomenology-HEP", "General Physics", "Experiment-HEP", "Other", "Experiment-Nucl", "Theory-Nucl" ];

        $scope.degree_types = [
          {value: 'Bachelor', text: 'Bachelor'},
          {value: 'Habilitation', text: 'Habilitation'},
          {value: 'Laurea', text: 'Laurea'},
          {value: 'Diploma', text: 'Diploma'},
          {value: 'Masters', text: 'Master'},
          {value: 'PhD', text: 'PhD'},
          {value: 'Thesis', text: 'Thesis'}
        ];

        $scope.doUpdate = function () {
          $scope.vm.update_ready = true;
          $scope.vm.saved = false;
          $scope.$emit();
        };

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

          addSubjectArea: function () {
            console.debug($scope.vm.new_subject_area);
            $scope.vm.record.metadata.field_categories.unshift({
              'scheme': "INSPIRE",
              'source': 'curator',
              'term': $scope.vm.new_subject_area,
              'accept': true
            });
            $scope.vm.new_subject_area = '';
            $scope.doUpdate();
          },

          addKeyword: function () {
            if (!$scope.vm.record._extra_data.keywords_prediction)
              $scope.vm.record._extra_data.keywords_prediction = {};

            if (!$scope.vm.record._extra_data.keywords_prediction.keywords)
              $scope.vm.record._extra_data.keywords_prediction.keywords = [];

            $scope.vm.record._extra_data.keywords_prediction.keywords.unshift({
              'score': 1.0,
              'label': $scope.vm.new_keyword,
              'accept': true
            });
            $scope.vm.new_keyword = '';
            $scope.doUpdate();
          },

          deleteSubject: function (index) {
            if (index < $scope.vm.record.metadata.field_categories.length)
              $scope.vm.record.metadata.field_categories.splice(index,1);
              $scope.doUpdate();
          },

          deleteRecord: function () {
            HoldingPenRecordService.deleteRecord($scope.vm, $scope.workflowId)
          },

          registerUpdateEvent: function () {
            $scope.doUpdate();
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

  function holdingPenTemplateHandler() {
    function templateUrl(element, attrs) {
      return attrs.template;
    }

    return {
      templateUrl: templateUrl,
      restrict: 'AE',
      scope: true
    };
  }

  function holdingPenDecision() {
    function templateUrl(element, attrs) {
      return attrs.template;
    }

    return {
      templateUrl: templateUrl,
      restrict: 'AE',
      scope: {
        Utils: "=utils",
        "record": "=record"
      }
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

  function autocomplete($timeout) {

    return function (scope, iElement, iAttrs) {
      var _item_id = iElement.attr("id");
      $("#" + iElement.attr("id")).autocomplete({
        source: scope.vm[iAttrs.uiItems],
        select: function (event, ui) {
          $timeout(function () {
            $(this).val((ui.item ? ui.item.value : ""));
            scope.vm[_item_id] = ui.item.value;
            $("#" + iElement.attr("id")).trigger('input');
          }, 0);
        }
      });

    };
  }

  angular.module('holdingpen.directives', [])
    .directive('holdingPenDecision', holdingPenDecision)
    .directive('holdingPen', holdingPenDetail)
    .directive('holdingPenBatchDecision', holdingPenBatchDecision)
    .directive('holdingPenDashboardItem', holdingPenDashboardItem)
    .directive('holdingPenTemplateHandler', holdingPenTemplateHandler)
    .directive('autocomplete', autocomplete);

})(angular);
