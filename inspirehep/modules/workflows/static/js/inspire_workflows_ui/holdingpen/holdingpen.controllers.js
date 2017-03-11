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

  function HoldingPenSelectionCtrl($scope, Hotkeys, HoldingPenRecordService, $window) {

    $scope.vm.selected_records = [];
    $scope.vm.selected_record_decisions = {};
    $scope.vm.selected_record_methods = {};

    $scope.toggleSelection = toggleSelection;
    $scope.toggleAll = toggleAll;
    $scope.isChecked = isChecked;
    $scope.allChecked = allChecked;
    $scope.setDecision = setDecision;
    $scope.redirect = redirect;

    function _add_record_method(record) {
      method = record._source.metadata.acquisition_source.method;
      if (method in $scope.vm.selected_record_methods) {
        $scope.vm.selected_record_methods[method]++;
      }
      else {
        $scope.vm.selected_record_methods[method] = 1;
      }
    }

    function _remove_record_method(record) {
      method = record._source.metadata.acquisition_source.method;
      $scope.vm.selected_record_methods[method]--;
    }

    function redirect(url) {
      $window.location = url;
    }

    function getItemIdx(id) {
      return $scope.vm.selected_records.indexOf(+id);
    }

    function toggleSelection(record) {
      var _data_type = record._source._workflow.data_type;

      if (isChecked(record._id)) {
        _remove_record_method(record);
        $scope.vm.selected_records.splice(getItemIdx(+record._id), 1);
        if (_data_type in $scope.vm.selected_record_decisions) {
          $scope.vm.selected_record_decisions[_data_type]
            .splice($scope.vm.selected_record_decisions[_data_type]
              .indexOf(+record._id), 1);
        }
      }
      else {
        _add_record_method(record);
        $scope.vm.selected_records.push(+record._id);
        if (_data_type) {
          if (!(_data_type in $scope.vm.selected_record_decisions)) {
            $scope.vm.selected_record_decisions[_data_type] = [];
          }
          if(record._source._extra_data === undefined ||
            record._source._extra_data.user_action == undefined)
            $scope.vm.selected_record_decisions[_data_type].push(+record._id);
        }
      }
    }

    function setDecision(id, decision) {
      HoldingPenRecordService.setBatchDecision(
        $scope.vm.invenioSearchResults.hits.hits, [+id], decision)
    }

    function toggleAll() {

      var remove_all = allChecked();
      if (remove_all) {
        reset();
      } else {
        angular.forEach($scope.$parent.vm.invenioSearchResults.hits.hits,
          function (record) {
            if (!isChecked(record._id)) {
              _add_record_method(record);
              $scope.vm.selected_records.push(+record._id);
              if (record._source._workflow.data_type) {
                if (!(record._source._workflow.data_type
                  in $scope.vm.selected_record_decisions)) {
                  $scope.vm.selected_record_decisions[
                    record._source._workflow.data_type] = [];
                }

                if(record._source._extra_data === undefined || record._source._extra_data.user_action == undefined)
                  $scope.vm.selected_record_decisions[record._source._workflow.data_type]
                    .push(record._id);
              }
            }
          });
      }
    }

    function isChecked(id) {
      return getItemIdx(+id) !== -1;
    }

    function allChecked() {
      if (!$scope.$parent.vm.invenioSearchResults.hits) {
        return false;
      }
      return $scope.vm.selected_records.length ===
        $scope.$parent.vm.invenioSearchResults.hits.hits.length;
    }

    function reset() {
      $scope.vm.selected_records = [];
      $scope.vm.selected_record_decisions = {};
      $scope.vm.selected_record_methods = [];
    }

    var hotkey = Hotkeys.createHotkey({
      key: 'ctrl+a',
      callback: function (e) {
        e.preventDefault();
        toggleAll();
      }
    });

    Hotkeys.registerHotkey(hotkey);

    $scope.$on('invenio.search.success', reset);
  }

  HoldingPenSelectionCtrl.$inject = ['$scope', 'Hotkeys', 'HoldingPenRecordService', '$window'];

  angular.module('holdingpen.controllers', [])
    .controller('HoldingPenSelectionCtrl', HoldingPenSelectionCtrl);

})(angular);
