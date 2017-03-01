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

    var controller = ["$scope", "HoldingPenRecordService", "$uibModal",
      function ($scope, HoldingPenRecordService, $uibModal) {

        $scope.modal = undefined;

        $scope.BatchUtils = {
          setDecision: function (type, decision) {
            console.debug($scope.vm.selected_record_decisions[type]);
            HoldingPenRecordService.setBatchDecision(
              $scope.vm.invenioSearchResults.hits.hits,
              $scope.vm.selected_record_decisions[type],
              decision)

            $scope.modal.dismiss('cancel');
          },

          showConfirm: function (data_type, operation) {
            $scope.data_type = data_type;
            $scope.operation = operation;

            $scope.modal = $uibModal.open({
              templateUrl: '/static/js/inspire_workflows_ui/templates/modals/batch_' + operation + '_modal.html'
            });
          },

          hideConfirm: function() {
            $scope.modal.dismiss('cancel')
          },

          restartWorkflows: function () {
            for (var select_record_idx in $scope.vm.selected_records) {
              HoldingPenRecordService.restartWorkflow($scope.vm, $scope.vm.selected_records[select_record_idx]);
            }
            $scope.vm.batch_message = $scope.vm.selected_records.length + " workflows restarted."
          },

          resumeWorkflows: function () {
            for (var select_record_idx in $scope.vm.selected_records) {
              HoldingPenRecordService.resumeWorkflow($scope.vm, $scope.vm.selected_records[select_record_idx]);
            }
            $scope.vm.batch_message = $scope.vm.selected_records.length + " workflows resumed.";
            $scope.modal.dismiss('cancel');
          },

          deleteWorkflows: function () {
            for (var select_record_idx in $scope.vm.selected_records) {
              HoldingPenRecordService.deleteRecord($scope.vm, $scope.vm.selected_records[select_record_idx], false);
            }
            window.location = '/holdingpen/list';
            $scope.vm.batch_message = $scope.vm.selected_records.length + " workflows deleted.";
            $scope.modal.dismiss('cancel');
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

    var controller = ["$scope", "HoldingPenRecordService", "$uibModal",  "$window",
      function ($scope, HoldingPenRecordService, $uibModal, $window) {
        $scope.vm = {};
        $scope.vm.loading = true;
        $scope.vm.new_subject_area = '';
        $scope.vm.new_keyword = '';
        $scope.vm.pdf_upload = true;

        $scope.vm.modal = undefined;

        $scope.vm.names = ["Astrophysics", "Computing", "Experiment-HEP", "Experiment-Nucl",
          "General Physics", "Gravitation and Cosmology", "Math and Math Physics", "Other", "Phenomenology-HEP", "Theory-HEP", "Theory-Nucl"];

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

          redirect: function (url) {
            $window.location = url;
          },

          addSubjectArea: function () {
            console.debug($scope.vm.new_subject_area);
            $scope.vm.record.metadata.inspire_categories.unshift({
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
            if (index < $scope.vm.record.metadata.inspire_categories.length)
              $scope.vm.record.metadata.inspire_categories.splice(index, 1);
            $scope.doUpdate();
          },

          deleteRecord: function () {
            HoldingPenRecordService.deleteRecord($scope.vm, $scope.workflowId, true)
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
        $scope.get_filter_string = function (extra_string=''){
          var query_string = ''
          if (extra_string !== '') {
              query_string = '?'
          }
          if ($scope.filterString !== undefined) {
              query_string = '?' + $scope.filterString + '&'
          }
          query_string += extra_string
          return query_string
        }
        $http.get('/api/holdingpen/'
                  + $scope.get_filter_string($scope.filterString))
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

            $scope.vm.class_name = $scope.sectionTitle.toLowerCase().replace(/ /g, "-")

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
        filterString: '@filterString',
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
